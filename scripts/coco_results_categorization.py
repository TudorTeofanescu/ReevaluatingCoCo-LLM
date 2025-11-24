#!/usr/bin/env python3
"""
CoCo Results Categorization Script

Categorizes CoCo analysis results with detailed timeout tracking:
- Vulnerable (with and without timeout, separated)
- Timeout (CoCo-enforced vs script-stopped)
- Parser Error (3 types with actual error messages)
- Successful (no separate report)

Written by Claude Code Assistant
"""

import os
import json
import shutil
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class ImprovedCoCoResultCategorizer:
    def __init__(self, source_dir: str):
        """
        Initialize the improved categorizer.

        Args:
            source_dir: Directory containing analyzed extensions
        """
        self.source_dir = Path(source_dir)

        # Base output directory
        self.base_output_dir = Path("DatasetCoCoCategorization")
        self.base_output_dir.mkdir(exist_ok=True)

        # Category directories
        self.vulnerable_dir = self.base_output_dir / "VulnerableExtensions"
        self.timeout_dir = self.base_output_dir / "TimeoutExtensions"
        self.parser_error_dir = self.base_output_dir / "ParserErrorExtensions"
        self.successful_dir = self.base_output_dir / "SuccessfulExtensions"

        # Create output directories
        self.vulnerable_dir.mkdir(exist_ok=True)
        self.timeout_dir.mkdir(exist_ok=True)
        self.parser_error_dir.mkdir(exist_ok=True)
        self.successful_dir.mkdir(exist_ok=True)

        # Results tracking
        self.results = {
            'scan_timestamp': datetime.now().isoformat(),
            'total_extensions_scanned': 0,

            # Vulnerable extensions
            'vulnerable_all': [],
            'vulnerable_no_timeout': [],
            'vulnerable_with_timeout': [],

            # Timeout without vulnerabilities
            'timeout_no_vuln': [],
            'timeout_coco_enforced': [],
            'timeout_script_stopped': [],

            # Parser errors
            'parser_errors': [],
            'parser_error_esprima': [],
            'parser_error_import': [],
            'parser_error_generation': [],

            # Successful
            'successful': [],

            # Statistics
            'vulnerability_sink_counts': {},
            'taint_type_extensions': {}
        }

    def log(self, message: str):
        """Print timestamped log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def run_analysis(self) -> Dict:
        """Run complete analysis on all extensions."""
        self.log("="*70)
        self.log("Improved CoCo Result Categorization")
        self.log("="*70)

        # Discover extensions
        all_extensions = self._discover_extensions()

        if not all_extensions:
            self.log("❌ No extensions found to process")
            return self.results

        total = len(all_extensions)
        self.log(f"📋 Found {total:,} extensions to categorize")
        self.log("")

        # Process all extensions
        self.log("🔄 Starting categorization...")
        self._process_all_extensions(all_extensions)

        # Generate reports
        self.log("")
        self.log("📊 Generating reports...")
        self._generate_reports()

        # Print summary
        self.print_summary()

        self.log("")
        self.log("✅ Categorization complete!")
        self.log("="*70)

        return self.results

    def _discover_extensions(self) -> List[Path]:
        """Discover all extensions to process"""
        if not self.source_dir.exists():
            self.log(f"❌ Source directory not found: {self.source_dir}")
            return []

        self.log(f"🔍 Scanning directory: {self.source_dir}")

        # Get all extension directories
        all_extensions = []
        for item in self.source_dir.iterdir():
            if item.is_dir():
                # Check if it has analysis output
                if (item / 'opgen_generated_files' / 'used_time.txt').exists():
                    all_extensions.append(item)

        # Sort for consistent processing
        all_extensions.sort(key=lambda x: x.name)

        return all_extensions

    def _process_all_extensions(self, extensions: List[Path]):
        """Process all extensions and categorize them"""
        total = len(extensions)

        for i, ext_dir in enumerate(extensions, 1):
            # Progress logging every 10,000 extensions
            if i % 10000 == 0 or i == 1:
                self.log(f"  Progress: {i:,}/{total:,} ({(i/total)*100:.1f}%)")

            self._categorize_extension(ext_dir)

        # Final progress
        self.log(f"  Progress: {total:,}/{total:,} (100.0%)")
        self.results['total_extensions_scanned'] = total

    def _categorize_extension(self, ext_dir: Path):
        """Categorize a single extension"""
        ext_id = ext_dir.name
        used_time_file = ext_dir / "opgen_generated_files" / "used_time.txt"

        if not used_time_file.exists():
            return

        try:
            with open(used_time_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Step 1: Check for parser errors (blocks everything else)
            parser_error_info = self._check_parser_errors(content, ext_id)
            if parser_error_info:
                self._record_parser_error(parser_error_info)
                return

            # Step 2: Check for vulnerabilities
            vulnerabilities = self._extract_vulnerabilities(content, ext_id)

            # Step 3: Check timeout type
            timeout_info = self._check_timeout_type(content)

            # Step 4: Categorize
            self._categorize_by_vuln_and_timeout(ext_dir, ext_id, vulnerabilities, timeout_info)

        except Exception as e:
            self.log(f"⚠️  Warning: Error processing {ext_id}: {e}")

    def _check_parser_errors(self, content: str, ext_id: str) -> Optional[Dict]:
        """Check if extension has parser errors"""
        parser_error_patterns = [
            (r'Error: [^\n]+ unexpected token while parsed with esprima', 'esprima_parse_error'),
            (r'Error: [^\n]+ can not import from string', 'import_from_string_error'),
            (r'Error: [^\n]+ in generating extension files', 'extension_generation_error')
        ]

        for pattern, error_type in parser_error_patterns:
            match = re.search(pattern, content)
            if match:
                return {
                    'extension_id': ext_id,
                    'error_type': error_type,
                    'error_message': match.group(0)
                }

        return None

    def _extract_vulnerabilities(self, content: str, ext_id: str) -> List[str]:
        """Extract vulnerability sink types from content"""
        vulnerabilities = set()

        # Pattern 1: "tainted detected!~~~in extension: ... with SINK_TYPE"
        primary_matches = re.findall(
            r'tainted detected!~~~in extension: [^~]+ with ([a-zA-Z0-9_.-]{3,50})',
            content
        )
        for sink_type in primary_matches:
            sink_type = sink_type.strip()
            if sink_type:
                vulnerabilities.add(sink_type)
                self._register_sink_type(sink_type, ext_id)

        # Pattern 2: "tainted detected!" followed by "with" in next lines
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'tainted detected!' in line:
                for j in range(i, min(i + 3, len(lines))):
                    with_match = re.search(r'with (.+)', lines[j])
                    if with_match:
                        sink_type = with_match.group(1).strip()
                        sink_type = re.split(r'[^a-zA-Z0-9_.-]', sink_type)[0]
                        if sink_type and 3 <= len(sink_type) <= 50:
                            vulnerabilities.add(sink_type)
                            self._register_sink_type(sink_type, ext_id)
                        break

        return list(vulnerabilities)

    def _check_timeout_type(self, content: str) -> Dict:
        """
        Check timeout type:
        - coco_enforced: Has "timeout after X seconds" marker
        - script_stopped: Has "analysis starts" but no "finish within" and no timeout marker
        - none: Has "finish within" marker
        """
        has_explicit_timeout = bool(re.search(r'timeout after \d+ seconds', content))
        has_start = 'analysis starts' in content or 'test_graph starts' in content
        has_finish = 'finish within' in content

        if has_explicit_timeout:
            # CoCo successfully caught and reported timeout
            duration_match = re.search(r'timeout after (\d+) seconds', content)
            return {
                'has_timeout': True,
                'timeout_type': 'coco_enforced',
                'timeout_duration': duration_match.group(1) if duration_match else 'unknown'
            }
        elif has_start and not has_finish:
            # Analysis started but no completion marker - mass analyzer killed it
            return {
                'has_timeout': True,
                'timeout_type': 'script_stopped',
                'timeout_duration': 'unknown'
            }
        else:
            # Completed normally
            return {
                'has_timeout': False,
                'timeout_type': None,
                'timeout_duration': None
            }

    def _categorize_by_vuln_and_timeout(self, ext_dir: Path, ext_id: str,
                                       vulnerabilities: List[str], timeout_info: Dict):
        """Categorize extension based on vulnerabilities and timeout"""
        has_vulns = len(vulnerabilities) > 0
        has_timeout = timeout_info['has_timeout']

        extension_info = {
            'extension_id': ext_id,
            'extension_path': str(ext_dir),
            'vulnerabilities': vulnerabilities,
            'vulnerability_count': len(vulnerabilities)
        }

        if has_vulns and has_timeout:
            # VULNERABLE + TIMEOUT
            extension_info.update({
                'timeout_type': timeout_info['timeout_type'],
                'timeout_duration': timeout_info['timeout_duration'],
                'partial_analysis': True
            })
            self.results['vulnerable_with_timeout'].append(extension_info)
            self.results['vulnerable_all'].append(extension_info)

            # Copy extension
            self._copy_extension(ext_dir, self.vulnerable_dir / ext_id)

        elif has_vulns and not has_timeout:
            # VULNERABLE ONLY (completed)
            extension_info['analysis_status'] = 'completed'
            self.results['vulnerable_no_timeout'].append(extension_info)
            self.results['vulnerable_all'].append(extension_info)

            # Copy extension
            self._copy_extension(ext_dir, self.vulnerable_dir / ext_id)

        elif not has_vulns and has_timeout:
            # TIMEOUT WITHOUT VULNERABILITIES
            extension_info.update({
                'timeout_type': timeout_info['timeout_type'],
                'timeout_duration': timeout_info['timeout_duration'],
                'vulnerabilities_found': 0
            })
            self.results['timeout_no_vuln'].append(extension_info)

            # Track by timeout type
            if timeout_info['timeout_type'] == 'coco_enforced':
                self.results['timeout_coco_enforced'].append(extension_info)
            else:
                self.results['timeout_script_stopped'].append(extension_info)

        else:
            # SUCCESSFUL (no vulns, no timeout, no errors)
            self.results['successful'].append({'extension_id': ext_id})

    def _record_parser_error(self, error_info: Dict):
        """Record parser error in appropriate category"""
        self.results['parser_errors'].append(error_info)

        error_type = error_info['error_type']
        if error_type == 'esprima_parse_error':
            self.results['parser_error_esprima'].append(error_info)
        elif error_type == 'import_from_string_error':
            self.results['parser_error_import'].append(error_info)
        elif error_type == 'extension_generation_error':
            self.results['parser_error_generation'].append(error_info)

    def _register_sink_type(self, sink_type: str, ext_id: str):
        """Register a sink type - tracks unique extensions per sink"""
        if sink_type not in self.results['taint_type_extensions']:
            self.results['taint_type_extensions'][sink_type] = []

        if ext_id not in self.results['taint_type_extensions'][sink_type]:
            self.results['taint_type_extensions'][sink_type].append(ext_id)

        # Count occurrences
        if sink_type not in self.results['vulnerability_sink_counts']:
            self.results['vulnerability_sink_counts'][sink_type] = 0
        self.results['vulnerability_sink_counts'][sink_type] += 1

    def _copy_extension(self, source_path: Path, dest_path: Path):
        """Copy extension directory"""
        try:
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.copytree(source_path, dest_path)
        except Exception as e:
            self.log(f"⚠️  Warning: Could not copy {source_path.name}: {e}")

    def _generate_reports(self):
        """Generate all JSON reports"""

        # 1. Vulnerable All Report (combined)
        self._generate_vulnerable_all_report()

        # 2. Vulnerable No Timeout Report
        self._generate_vulnerable_no_timeout_report()

        # 3. Vulnerable With Timeout Report
        self._generate_vulnerable_with_timeout_report()

        # 4. Timeout Report (no vulnerabilities)
        self._generate_timeout_report()

        # 5. Parser Error Report
        self._generate_parser_error_report()

        # 6. Comprehensive Analysis Report
        self._generate_comprehensive_report()

    def _generate_vulnerable_all_report(self):
        """Generate combined vulnerable extensions report"""
        report_file = self.vulnerable_dir / "vulnerable_all_report.json"

        # Calculate sink type counts
        sink_type_counts = {k: len(v) for k, v in self.results['taint_type_extensions'].items()}

        report = {
            'scan_timestamp': self.results['scan_timestamp'],
            'total_vulnerable_extensions': len(self.results['vulnerable_all']),
            'breakdown': {
                'vulnerable_no_timeout': len(self.results['vulnerable_no_timeout']),
                'vulnerable_with_timeout': len(self.results['vulnerable_with_timeout'])
            },
            'all_vulnerable_extension_ids': [ext['extension_id'] for ext in self.results['vulnerable_all']],
            'vulnerability_summary': {
                'total_unique_sink_types': len(self.results['taint_type_extensions']),
                'sink_type_counts': sink_type_counts
            },
            'per_extension_details': self.results['vulnerable_all']
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log("  ✓ vulnerable_all_report.json")

    def _generate_vulnerable_no_timeout_report(self):
        """Generate vulnerable without timeout report"""
        report_file = self.vulnerable_dir / "vulnerable_no_timeout_report.json"

        # Calculate sink type counts for this subset
        sink_counts = {}
        for ext in self.results['vulnerable_no_timeout']:
            for sink in ext['vulnerabilities']:
                sink_counts[sink] = sink_counts.get(sink, 0) + 1

        report = {
            'scan_timestamp': self.results['scan_timestamp'],
            'total_vulnerable_no_timeout': len(self.results['vulnerable_no_timeout']),
            'extension_ids': [ext['extension_id'] for ext in self.results['vulnerable_no_timeout']],
            'vulnerability_summary': {
                'total_unique_sink_types': len(sink_counts),
                'sink_type_counts': sink_counts
            },
            'per_extension_details': self.results['vulnerable_no_timeout']
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log("  ✓ vulnerable_no_timeout_report.json")

    def _generate_vulnerable_with_timeout_report(self):
        """Generate vulnerable with timeout report"""
        report_file = self.vulnerable_dir / "vulnerable_with_timeout_report.json"

        # Split by timeout type
        coco_enforced = [ext for ext in self.results['vulnerable_with_timeout']
                        if ext.get('timeout_type') == 'coco_enforced']
        script_stopped = [ext for ext in self.results['vulnerable_with_timeout']
                         if ext.get('timeout_type') == 'script_stopped']

        # Calculate sink type counts
        sink_counts = {}
        for ext in self.results['vulnerable_with_timeout']:
            for sink in ext['vulnerabilities']:
                sink_counts[sink] = sink_counts.get(sink, 0) + 1

        report = {
            'scan_timestamp': self.results['scan_timestamp'],
            'total_vulnerable_with_timeout': len(self.results['vulnerable_with_timeout']),
            'timeout_breakdown': {
                'coco_enforced_timeout': {
                    'count': len(coco_enforced),
                    'extension_ids': [ext['extension_id'] for ext in coco_enforced]
                },
                'script_stopped_coco': {
                    'count': len(script_stopped),
                    'extension_ids': [ext['extension_id'] for ext in script_stopped]
                }
            },
            'all_extension_ids': [ext['extension_id'] for ext in self.results['vulnerable_with_timeout']],
            'vulnerability_summary': {
                'total_unique_sink_types': len(sink_counts),
                'sink_type_counts': sink_counts
            },
            'per_extension_details': self.results['vulnerable_with_timeout']
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log("  ✓ vulnerable_with_timeout_report.json")

    def _generate_timeout_report(self):
        """Generate timeout without vulnerabilities report"""
        report_file = self.timeout_dir / "timeout_report.json"

        report = {
            'scan_timestamp': self.results['scan_timestamp'],
            'total_timeout_no_vulnerabilities': len(self.results['timeout_no_vuln']),
            'timeout_breakdown': {
                'coco_enforced_timeout': {
                    'total': len(self.results['timeout_coco_enforced']),
                    'extension_ids': [ext['extension_id'] for ext in self.results['timeout_coco_enforced']]
                },
                'script_stopped_coco': {
                    'total': len(self.results['timeout_script_stopped']),
                    'extension_ids': [ext['extension_id'] for ext in self.results['timeout_script_stopped']]
                }
            },
            'all_extension_ids': [ext['extension_id'] for ext in self.results['timeout_no_vuln']],
            'per_extension_details': self.results['timeout_no_vuln']
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log("  ✓ timeout_report.json")

    def _generate_parser_error_report(self):
        """Generate parser error report with actual error messages"""
        report_file = self.parser_error_dir / "parser_error_report.json"

        # Collect sample errors for each type
        sample_errors = {
            'esprima_parse_error': [],
            'import_from_string_error': [],
            'extension_generation_error': []
        }

        for error in self.results['parser_errors']:
            error_type = error['error_type']
            if len(sample_errors[error_type]) < 5:  # Keep first 5 samples
                sample_errors[error_type].append(error['error_message'])

        report = {
            'scan_timestamp': self.results['scan_timestamp'],
            'total_parser_errors': len(self.results['parser_errors']),
            'error_breakdown': {
                'esprima_parse_error': {
                    'total': len(self.results['parser_error_esprima']),
                    'extension_ids': [err['extension_id'] for err in self.results['parser_error_esprima']],
                    'sample_errors': sample_errors['esprima_parse_error']
                },
                'import_from_string_error': {
                    'total': len(self.results['parser_error_import']),
                    'extension_ids': [err['extension_id'] for err in self.results['parser_error_import']],
                    'sample_errors': sample_errors['import_from_string_error']
                },
                'extension_generation_error': {
                    'total': len(self.results['parser_error_generation']),
                    'extension_ids': [err['extension_id'] for err in self.results['parser_error_generation']],
                    'sample_errors': sample_errors['extension_generation_error']
                }
            },
            'all_extension_ids': [err['extension_id'] for err in self.results['parser_errors']],
            'per_extension_details': self.results['parser_errors']
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log("  ✓ parser_error_report.json")

    def _generate_comprehensive_report(self):
        """Generate comprehensive overview report"""
        report_file = self.base_output_dir / "comprehensive_analysis_report.json"

        total = self.results['total_extensions_scanned']

        # Calculate timeout totals
        total_timeouts = len(self.results['vulnerable_with_timeout']) + len(self.results['timeout_no_vuln'])
        coco_enforced_total = len([e for e in self.results['vulnerable_with_timeout']
                                   if e.get('timeout_type') == 'coco_enforced']) + \
                             len(self.results['timeout_coco_enforced'])
        script_stopped_total = len([e for e in self.results['vulnerable_with_timeout']
                                    if e.get('timeout_type') == 'script_stopped']) + \
                              len(self.results['timeout_script_stopped'])

        # Top 10 sinks
        sink_type_counts = {k: len(v) for k, v in self.results['taint_type_extensions'].items()}
        top_10_sinks = sorted(sink_type_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        report = {
            'scan_timestamp': self.results['scan_timestamp'],
            'dataset_info': {
                'total_extensions_analyzed': total,
                'analysis_complete': True
            },
            'category_breakdown': {
                'vulnerable': {
                    'total': len(self.results['vulnerable_all']),
                    'vulnerable_no_timeout': len(self.results['vulnerable_no_timeout']),
                    'vulnerable_with_timeout': len(self.results['vulnerable_with_timeout']),
                    'percentage': f"{(len(self.results['vulnerable_all']) / max(1, total)) * 100:.2f}%"
                },
                'timeout_no_vuln': {
                    'total': len(self.results['timeout_no_vuln']),
                    'coco_enforced': len(self.results['timeout_coco_enforced']),
                    'script_stopped': len(self.results['timeout_script_stopped']),
                    'percentage': f"{(len(self.results['timeout_no_vuln']) / max(1, total)) * 100:.2f}%"
                },
                'parser_errors': {
                    'total': len(self.results['parser_errors']),
                    'esprima_parse_error': len(self.results['parser_error_esprima']),
                    'import_from_string_error': len(self.results['parser_error_import']),
                    'extension_generation_error': len(self.results['parser_error_generation']),
                    'percentage': f"{(len(self.results['parser_errors']) / max(1, total)) * 100:.2f}%"
                },
                'successful': {
                    'total': len(self.results['successful']),
                    'percentage': f"{(len(self.results['successful']) / max(1, total)) * 100:.2f}%"
                }
            },
            'timeout_overview': {
                'total_timeouts': total_timeouts,
                'with_vulnerabilities': len(self.results['vulnerable_with_timeout']),
                'without_vulnerabilities': len(self.results['timeout_no_vuln']),
                'coco_enforced_total': coco_enforced_total,
                'script_stopped_total': script_stopped_total
            },
            'vulnerability_overview': {
                'total_vulnerable_extensions': len(self.results['vulnerable_all']),
                'total_unique_sink_types': len(self.results['taint_type_extensions']),
                'total_taint_flows_detected': sum(self.results['vulnerability_sink_counts'].values()),
                'top_10_sinks': [
                    {
                        'sink': sink,
                        'extensions': count,
                        'flows': self.results['vulnerability_sink_counts'].get(sink, 0)
                    }
                    for sink, count in top_10_sinks
                ]
            }
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log("  ✓ comprehensive_analysis_report.json")

    def print_summary(self):
        """Print comprehensive summary"""
        self.log("")
        self.log("="*70)
        self.log("CATEGORIZATION SUMMARY")
        self.log("="*70)

        total = self.results['total_extensions_scanned']

        self.log(f"Total extensions analyzed:           {total:,}")
        self.log("")

        # Vulnerable
        vuln_total = len(self.results['vulnerable_all'])
        vuln_no_timeout = len(self.results['vulnerable_no_timeout'])
        vuln_with_timeout = len(self.results['vulnerable_with_timeout'])
        self.log(f"🚨 VULNERABLE:                        {vuln_total:,} ({(vuln_total/max(1,total))*100:.2f}%)")
        self.log(f"   ├─ Without Timeout:                {vuln_no_timeout:,} ({(vuln_no_timeout/max(1,vuln_total))*100:.1f}% of vulnerable)")
        self.log(f"   └─ With Timeout:                   {vuln_with_timeout:,} ({(vuln_with_timeout/max(1,vuln_total))*100:.1f}% of vulnerable)")

        # Timeout breakdown for vulnerable
        if vuln_with_timeout > 0:
            coco_vuln = len([e for e in self.results['vulnerable_with_timeout'] if e.get('timeout_type') == 'coco_enforced'])
            script_vuln = len([e for e in self.results['vulnerable_with_timeout'] if e.get('timeout_type') == 'script_stopped'])
            self.log(f"      ├─ CoCo Enforced:               {coco_vuln:,}")
            self.log(f"      └─ Script Stopped:              {script_vuln:,}")

        self.log("")

        # Timeout no vuln
        timeout_total = len(self.results['timeout_no_vuln'])
        timeout_coco = len(self.results['timeout_coco_enforced'])
        timeout_script = len(self.results['timeout_script_stopped'])
        self.log(f"⏱️  TIMEOUT (no vuln):                {timeout_total:,} ({(timeout_total/max(1,total))*100:.2f}%)")
        self.log(f"   ├─ CoCo Enforced:                  {timeout_coco:,} ({(timeout_coco/max(1,timeout_total))*100:.1f}%)")
        self.log(f"   └─ Script Stopped:                 {timeout_script:,} ({(timeout_script/max(1,timeout_total))*100:.1f}%)")
        self.log("")

        # Parser errors
        parser_total = len(self.results['parser_errors'])
        parser_esprima = len(self.results['parser_error_esprima'])
        parser_import = len(self.results['parser_error_import'])
        parser_gen = len(self.results['parser_error_generation'])
        self.log(f"❌ PARSER ERROR:                      {parser_total:,} ({(parser_total/max(1,total))*100:.2f}%)")
        self.log(f"   ├─ Esprima Parse Error:            {parser_esprima:,} ({(parser_esprima/max(1,parser_total))*100:.1f}%)")
        self.log(f"   ├─ Import Error:                   {parser_import:,} ({(parser_import/max(1,parser_total))*100:.1f}%)")
        self.log(f"   └─ Generation Error:               {parser_gen:,} ({(parser_gen/max(1,parser_total))*100:.1f}%)")
        self.log("")

        # Successful
        success_total = len(self.results['successful'])
        self.log(f"✅ SUCCESSFUL:                        {success_total:,} ({(success_total/max(1,total))*100:.2f}%)")
        self.log("")

        # Overall timeout statistics
        all_timeouts = vuln_with_timeout + timeout_total
        all_coco = len([e for e in self.results['vulnerable_with_timeout'] if e.get('timeout_type') == 'coco_enforced']) + timeout_coco
        all_script = len([e for e in self.results['vulnerable_with_timeout'] if e.get('timeout_type') == 'script_stopped']) + timeout_script
        self.log(f"TIMEOUT TOTAL:                        {all_timeouts:,} (vulnerable + no vuln)")
        self.log(f"   ├─ CoCo Enforced:                  {all_coco:,}")
        self.log(f"   └─ Script Stopped:                 {all_script:,}")

        self.log("="*70)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Improved CoCo Results Categorization')
    parser.add_argument('--source', default='source_extensions',
                        help='Source directory with analyzed extensions (default: source_extensions)')

    args = parser.parse_args()

    try:
        categorizer = ImprovedCoCoResultCategorizer(source_dir=args.source)
        categorizer.run_analysis()
        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
