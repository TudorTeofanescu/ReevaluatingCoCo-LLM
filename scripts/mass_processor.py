#!/usr/bin/env python3
"""
Server Mass Processor for CoCo Analysis 
Production-ready with progress tracking, logging, and resumption

Written by Claude Code Assistant
"""

import os
import sys
import json
import time
import signal
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Set
import logging
from datetime import datetime
import threading
import hashlib

@dataclass
class ExtensionResult:
    """Container for extension analysis results"""
    extension_id: str
    success: bool
    processing_time: float
    return_code: int
    vulnerabilities: int
    vulnerability_types: List[str]
    timestamp: str
    worker_id: str
    stdout_hash: str = ""
    stderr_preview: str = ""

class ServerMassProcessor:
    """Production mass processor for 195k extensions"""
    
    def __init__(self, 
                 source_dir: str = "source_extensions",
                 max_workers: int = 50,
                 timeout: int = 600,
                 batch_size: int = 1000):
        
        # Paths - adapted for server environment
        self.script_dir = Path(__file__).parent
        self.source_dir = (self.script_dir / source_dir).resolve()
        self.coco_dir = (self.script_dir / "CoCo").resolve()
        self.venv_python = (self.script_dir / "cwsCoCoEnv" / "bin" / "python3").resolve()
        
        # Server configuration
        self.max_workers = max_workers
        self.timeout = timeout
        self.batch_size = batch_size
        
        # Logging and progress tracking
        self.logs_dir = self.script_dir / "logs"
        self.results_dir = self.script_dir / "results"
        self.progress_file = self.logs_dir / "progress.json"
        self.processed_file = self.logs_dir / "processed_extensions.txt"
        
        # Create directories
        self.logs_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        
        # Statistics
        self.stats = {
            'total_discovered': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'vulnerabilities_found': 0,
            'start_time': None,
            'last_update': None,
            'current_batch': 0
        }
        
        # Thread safety
        self.stats_lock = threading.Lock()
        self.processed_extensions: Set[str] = set()
        
        # Setup logging
        self.setup_logging()
        
        # Signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        # Load previous progress
        self.load_progress()
    
    def setup_logging(self):
        """Setup comprehensive logging system"""
        # Main log file
        main_log = self.logs_dir / f"mass_processor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Progress log (lightweight)
        progress_log = self.logs_dir / "progress.log"
        
        # Error log (failures only)
        error_log = self.logs_dir / "errors.log"
        
        # Configure main logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(main_log),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('MassProcessor')
        
        # Progress logger (separate)
        self.progress_logger = logging.getLogger('Progress')
        progress_handler = logging.FileHandler(progress_log)
        progress_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.progress_logger.addHandler(progress_handler)
        self.progress_logger.setLevel(logging.INFO)
        
        # Error logger (separate)
        self.error_logger = logging.getLogger('Errors')
        error_handler = logging.FileHandler(error_log)
        error_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.error_logger.addHandler(error_handler)
        self.error_logger.setLevel(logging.ERROR)
    
    def load_progress(self):
        """Load previous progress from files"""
        # Load processed extensions list
        if self.processed_file.exists():
            with open(self.processed_file, 'r') as f:
                self.processed_extensions = set(line.strip() for line in f if line.strip())
            self.logger.info(f"Loaded {len(self.processed_extensions)} previously processed extensions")
        
        # Load progress stats
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    saved_stats = json.load(f)
                    self.stats.update(saved_stats)
                    self.logger.info(f"Loaded progress: {self.stats['processed']} processed, {self.stats['successful']} successful")
            except Exception as e:
                self.logger.warning(f"Could not load progress file: {e}")
    
    def save_progress(self):
        """Save current progress to files"""
        with self.stats_lock:
            # Save stats
            progress_data = {
                **self.stats,
                'timestamp': datetime.now().isoformat(),
                'processed_extensions_count': len(self.processed_extensions)
            }

            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)

            # Overwrite with current processed extensions (no duplicates)
            with open(self.processed_file, 'w') as f:
                for ext_id in self.processed_extensions:
                    f.write(f"{ext_id}\n")
    
    def discover_extensions(self, limit: Optional[int] = None) -> List[Path]:
        """Discover extensions, excluding already processed ones"""
        if not self.source_dir.exists():
            self.logger.error(f"Source directory not found: {self.source_dir}")
            return []
        
        self.logger.info(f"Discovering extensions in {self.source_dir}")
        
        # Get all extension directories
        all_extensions = []
        for item in self.source_dir.iterdir():
            if item.is_dir() and (item / 'manifest.json').exists():
                extension_id = item.name
                if extension_id not in self.processed_extensions:
                    all_extensions.append(item)
        
        # Sort for consistent ordering
        all_extensions.sort(key=lambda x: x.name)
        
        # Apply limit
        if limit:
            all_extensions = all_extensions[:limit]
        
        with self.stats_lock:
            self.stats['total_discovered'] = len(all_extensions)
        
        self.logger.info(f"Discovered {len(all_extensions)} new extensions to process")
        self.logger.info(f"Previously processed: {len(self.processed_extensions)} extensions")
        
        return all_extensions
    
    def analyze_extension(self, extension_path: Path) -> ExtensionResult:
        """Analyze single extension using shell wrapper"""
        extension_id = extension_path.name
        start_time = time.time()
        worker_id = threading.current_thread().ident
        
        # Build command using shell wrapper
        cmd = [
            str(self.script_dir / "run_coco.sh"),
            "-t", "chrome_ext",
            "-crx",
            "--timeout", str(self.timeout),
            str(extension_path)
        ]
        
        self.logger.debug(f"Worker {worker_id} analyzing {extension_id}")
        
        try:
            # Run CoCo analysis
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 30  # Extra buffer
            )
            
            processing_time = time.time() - start_time
            
            # Parse vulnerabilities
            vulnerabilities = 0
            vulnerability_types = []
            
            if result.returncode == 0 and result.stdout:
                # Count vulnerabilities
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'tainted detected' in line.lower():
                        vulnerabilities += 1
                        # Extract vulnerability type if possible
                        if 'with ' in line:
                            vuln_type = line.split('with ')[-1].strip()
                            if vuln_type not in vulnerability_types:
                                vulnerability_types.append(vuln_type)
            
            # Create result
            extension_result = ExtensionResult(
                extension_id=extension_id,
                success=result.returncode == 0,
                processing_time=processing_time,
                return_code=result.returncode,
                vulnerabilities=vulnerabilities,
                vulnerability_types=vulnerability_types,
                timestamp=datetime.now().isoformat(),
                worker_id=str(worker_id),
                stdout_hash=hashlib.md5(result.stdout.encode()).hexdigest() if result.stdout else "",
                stderr_preview=result.stderr[:200] if result.stderr else ""
            )
            
            # Log result
            if extension_result.success:
                self.logger.info(f"✅ {extension_id} - {processing_time:.1f}s - {vulnerabilities} vulnerabilities")
                self.progress_logger.info(f"SUCCESS {extension_id} {processing_time:.1f}s {vulnerabilities}vulns")
            else:
                self.logger.warning(f"❌ {extension_id} - {processing_time:.1f}s - Failed (code: {result.returncode})")
                self.error_logger.error(f"FAILED {extension_id} code:{result.returncode} {extension_result.stderr_preview}")
            
            # Update stats
            with self.stats_lock:
                self.stats['processed'] += 1
                if extension_result.success:
                    self.stats['successful'] += 1
                    self.stats['vulnerabilities_found'] += vulnerabilities
                else:
                    self.stats['failed'] += 1
                
                self.processed_extensions.add(extension_id)
            
            return extension_result
            
        except subprocess.TimeoutExpired:
            processing_time = time.time() - start_time
            self.logger.warning(f"⏰ {extension_id} - Timeout after {processing_time:.1f}s")
            self.error_logger.error(f"TIMEOUT {extension_id} {processing_time:.1f}s")
            
            with self.stats_lock:
                self.stats['processed'] += 1
                self.stats['failed'] += 1
                self.processed_extensions.add(extension_id)
            
            return ExtensionResult(
                extension_id=extension_id,
                success=False,
                processing_time=processing_time,
                return_code=-1,
                vulnerabilities=0,
                vulnerability_types=[],
                timestamp=datetime.now().isoformat(),
                worker_id=str(worker_id),
                stderr_preview="Timeout expired"
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"💥 {extension_id} - Error: {e}")
            self.error_logger.error(f"ERROR {extension_id} {str(e)}")
            
            with self.stats_lock:
                self.stats['processed'] += 1
                self.stats['failed'] += 1
                self.processed_extensions.add(extension_id)
            
            return ExtensionResult(
                extension_id=extension_id,
                success=False,
                processing_time=processing_time,
                return_code=-2,
                vulnerabilities=0,
                vulnerability_types=[],
                timestamp=datetime.now().isoformat(),
                worker_id=str(worker_id),
                stderr_preview=str(e)
            )
    
    def run_batch(self, extensions: List[Path]):
        """Process a batch of extensions"""
        if not extensions:
            self.logger.info("No extensions to process")
            return
        
        self.logger.info(f"🚀 Starting batch processing")
        self.logger.info(f"📊 Extensions: {len(extensions)}")
        self.logger.info(f"👷 Workers: {self.max_workers}")
        self.logger.info(f"⏱️  Timeout: {self.timeout}s per extension")
        
        with self.stats_lock:
            self.stats['start_time'] = time.time()
        
        # Process with ThreadPoolExecutor
        batch_results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all jobs
            future_to_extension = {
                executor.submit(self.analyze_extension, ext): ext
                for ext in extensions
            }
            
            # Process results as they complete
            for future in as_completed(future_to_extension):
                try:
                    result = future.result()
                    batch_results.append(result)
                    
                    # Progress reporting every 100 extensions
                    if len(batch_results) % 100 == 0:
                        self.print_progress(len(batch_results), len(extensions))
                        self.save_progress()
                    
                except Exception as e:
                    extension = future_to_extension[future]
                    self.logger.error(f"Future error for {extension.name}: {e}")
        
        # Save batch results
        self.save_batch_results(batch_results)
        
        # Final progress
        self.print_final_stats(batch_results)
        self.save_progress()
    
    def print_progress(self, current: int, total: int):
        """Print progress update"""
        with self.stats_lock:
            elapsed = time.time() - self.stats['start_time']
            rate = current / elapsed if elapsed > 0 else 0
            remaining = total - current
            eta = remaining / rate / 60 if rate > 0 else 0
            
            success_rate = self.stats['successful'] / max(1, self.stats['processed']) * 100
            
            progress_msg = (
                f"📈 Progress: {current}/{total} ({current/total*100:.1f}%) | "
                f"Success: {success_rate:.1f}% | "
                f"Rate: {rate:.1f}/s | "
                f"Vulnerabilities: {self.stats['vulnerabilities_found']} | "
                f"ETA: {eta:.1f}min"
            )
            
            self.logger.info(progress_msg)
            self.progress_logger.info(progress_msg)
    
    def print_final_stats(self, batch_results: List[ExtensionResult]):
        """Print final batch statistics"""
        total_time = time.time() - self.stats['start_time']
        
        successful = [r for r in batch_results if r.success]
        failed = [r for r in batch_results if not r.success]
        
        self.logger.info("=" * 60)
        self.logger.info(f"🎉 Batch processing completed in {total_time/60:.1f} minutes")
        self.logger.info(f"📊 Results: {len(successful)}/{len(batch_results)} successful ({len(successful)/len(batch_results)*100:.1f}%)")
        self.logger.info(f"🔍 Vulnerabilities found: {sum(r.vulnerabilities for r in successful)}")
        self.logger.info(f"⚡ Average processing time: {sum(r.processing_time for r in successful)/len(successful):.1f}s")
        
        # Top vulnerable extensions
        top_vulnerable = sorted(successful, key=lambda x: x.vulnerabilities, reverse=True)[:10]
        if top_vulnerable:
            self.logger.info("🏆 Top 10 most vulnerable extensions:")
            for i, ext in enumerate(top_vulnerable, 1):
                self.logger.info(f"  {i}. {ext.extension_id}: {ext.vulnerabilities} vulnerabilities")
        
        self.logger.info("=" * 60)
    
    def save_batch_results(self, results: List[ExtensionResult]):
        """Save batch results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = self.results_dir / f"batch_results_{timestamp}.json"
        
        # Convert results to dict format
        results_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'batch_size': len(results),
                'successful': len([r for r in results if r.success]),
                'failed': len([r for r in results if not r.success]),
                'total_vulnerabilities': sum(r.vulnerabilities for r in results if r.success)
            },
            'results': [asdict(result) for result in results]
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        self.logger.info(f"💾 Batch results saved to {results_file}")
    
    def shutdown(self, signum, frame):
        """Graceful shutdown"""
        self.logger.info("🛑 Shutdown signal received. Saving progress...")
        self.save_progress()
        self.logger.info("✅ Progress saved. Exiting.")
        sys.exit(0)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Server Mass Processor for CoCo Analysis')
    parser.add_argument('--source-dir', default='source_extensions', help='Source directory with extensions')
    parser.add_argument('--workers', type=int, default=50, help='Number of worker threads')
    parser.add_argument('--timeout', type=int, default=600, help='Timeout per extension (seconds)')
    parser.add_argument('--limit', type=int, help='Limit number of extensions to process')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for processing')
    
    args = parser.parse_args()
    
    # Create processor
    processor = ServerMassProcessor(
        source_dir=args.source_dir,
        max_workers=args.workers,
        timeout=args.timeout,
        batch_size=args.batch_size
    )
    
    # Discover extensions
    extensions = processor.discover_extensions(args.limit)
    
    if not extensions:
        processor.logger.info("No new extensions found to process")
        return
    
    # Process extensions
    processor.run_batch(extensions)
    
    processor.logger.info("🎉 Mass processing completed successfully")

if __name__ == "__main__":
    main()