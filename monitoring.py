# Performance Monitoring and Analytics for Bus Ticket Booking System

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, deque
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available, system monitoring will be limited")

class PerformanceMonitor:
    """Monitor system performance and API metrics"""
    
    def __init__(self, max_records: int = 1000):
        self.max_records = max_records
        self.request_times = deque(maxlen=max_records)
        self.endpoint_stats = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.active_requests = 0
        self.start_time = datetime.now()
        self.system_stats = {}
        self._monitoring_thread = None
        self._stop_monitoring = False
        
        # Start system monitoring
        self.start_system_monitoring()
    
    def start_system_monitoring(self):
        """Start background system monitoring"""
        self._monitoring_thread = threading.Thread(target=self._monitor_system)
        self._monitoring_thread.daemon = True
        self._monitoring_thread.start()
    
    def _monitor_system(self):
        """Monitor system resources in background"""
        while not self._stop_monitoring:
            try:
                if PSUTIL_AVAILABLE:
                    # Get CPU and memory usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    # Get network stats if available
                    try:
                        network = psutil.net_io_counters()
                        network_stats = {
                            'bytes_sent': network.bytes_sent,
                            'bytes_recv': network.bytes_recv,
                            'packets_sent': network.packets_sent,
                            'packets_recv': network.packets_recv
                        }
                    except:
                        network_stats = {}
                    
                    self.system_stats = {
                        'timestamp': datetime.now().isoformat(),
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'memory_available': memory.available,
                        'memory_total': memory.total,
                        'disk_percent': disk.percent,
                        'disk_free': disk.free,
                        'disk_total': disk.total,
                        'network': network_stats,
                        'active_requests': self.active_requests
                    }
                else:
                    # Fallback when psutil is not available
                    self.system_stats = {
                        'timestamp': datetime.now().isoformat(),
                        'cpu_percent': 0,
                        'memory_percent': 0,
                        'memory_available': 0,
                        'memory_total': 0,
                        'disk_percent': 0,
                        'disk_free': 0,
                        'disk_total': 0,
                        'network': {},
                        'active_requests': self.active_requests,
                        'note': 'Limited monitoring - psutil not available'
                    }
                
                time.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error monitoring system: {e}")
                time.sleep(60)
    
    def record_request(self, endpoint: str, method: str, duration: float, 
                      status_code: int = 200):
        """Record API request metrics"""
        timestamp = datetime.now()
        
        # Record request time
        request_data = {
            'endpoint': endpoint,
            'method': method,
            'duration': duration,
            'status_code': status_code,
            'timestamp': timestamp
        }
        
        self.request_times.append(request_data)
        self.endpoint_stats[f"{method} {endpoint}"].append(duration)
        
        # Record errors
        if status_code >= 400:
            self.error_counts[f"{status_code}"] += 1
    
    def start_request(self):
        """Mark start of a request"""
        self.active_requests += 1
    
    def end_request(self):
        """Mark end of a request"""
        self.active_requests = max(0, self.active_requests - 1)
    
    def get_performance_stats(self) -> Dict:
        """Get comprehensive performance statistics"""
        now = datetime.now()
        uptime = now - self.start_time
        
        # Calculate response time statistics
        if self.request_times:
            durations = [req['duration'] for req in self.request_times]
            avg_response_time = sum(durations) / len(durations)
            max_response_time = max(durations)
            min_response_time = min(durations)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        # Calculate requests per minute
        recent_requests = [
            req for req in self.request_times 
            if now - req['timestamp'] <= timedelta(minutes=1)
        ]
        requests_per_minute = len(recent_requests)
        
        # Get endpoint statistics
        endpoint_stats = {}
        for endpoint, durations in self.endpoint_stats.items():
            if durations:
                endpoint_stats[endpoint] = {
                    'count': len(durations),
                    'avg_duration': sum(durations) / len(durations),
                    'max_duration': max(durations),
                    'min_duration': min(durations)
                }
        
        return {
            'system': self.system_stats,
            'uptime': str(uptime).split('.')[0],
            'total_requests': len(self.request_times),
            'active_requests': self.active_requests,
            'requests_per_minute': requests_per_minute,
            'response_times': {
                'average': round(avg_response_time, 3),
                'maximum': round(max_response_time, 3),
                'minimum': round(min_response_time, 3)
            },
            'endpoints': endpoint_stats,
            'errors': dict(self.error_counts),
            'error_rate': self.calculate_error_rate()
        }
    
    def calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        if not self.request_times:
            return 0.0
        
        total_requests = len(self.request_times)
        error_requests = sum(
            1 for req in self.request_times 
            if req['status_code'] >= 400
        )
        
        return round((error_requests / total_requests) * 100, 2)
    
    def get_health_status(self) -> Dict:
        """Get system health status"""
        stats = self.get_performance_stats()
        
        # Determine health status based on metrics
        health_status = "healthy"
        issues = []
        
        # Check CPU usage
        if stats['system'].get('cpu_percent', 0) > 80:
            health_status = "degraded"
            issues.append("High CPU usage")
        
        # Check memory usage
        if stats['system'].get('memory_percent', 0) > 85:
            health_status = "degraded"
            issues.append("High memory usage")
        
        # Check disk usage
        if stats['system'].get('disk_percent', 0) > 90:
            health_status = "degraded"
            issues.append("High disk usage")
        
        # Check error rate
        if stats['error_rate'] > 10:
            health_status = "unhealthy"
            issues.append("High error rate")
        
        # Check response times
        if stats['response_times']['average'] > 5:
            health_status = "degraded"
            issues.append("Slow response times")
        
        return {
            'status': health_status,
            'issues': issues,
            'timestamp': datetime.now().isoformat()
        }
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self._stop_monitoring = True
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)


class APIAnalytics:
    """Analytics for API usage patterns"""
    
    def __init__(self):
        self.daily_usage = defaultdict(int)
        self.hourly_usage = defaultdict(int)
        self.popular_endpoints = defaultdict(int)
        self.user_agents = defaultdict(int)
        self.ip_addresses = defaultdict(int)
    
    def record_api_call(self, endpoint: str, user_agent: str = '', 
                       ip_address: str = ''):
        """Record API call for analytics"""
        now = datetime.now()
        
        # Record daily usage
        date_key = now.strftime('%Y-%m-%d')
        self.daily_usage[date_key] += 1
        
        # Record hourly usage
        hour_key = now.strftime('%H')
        self.hourly_usage[hour_key] += 1
        
        # Record endpoint popularity
        self.popular_endpoints[endpoint] += 1
        
        # Record user agents
        if user_agent:
            self.user_agents[user_agent] += 1
        
        # Record IP addresses
        if ip_address:
            self.ip_addresses[ip_address] += 1
    
    def get_analytics_report(self) -> Dict:
        """Get comprehensive analytics report"""
        # Get top endpoints
        top_endpoints = sorted(
            self.popular_endpoints.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Get peak hours
        peak_hours = sorted(
            self.hourly_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Get recent daily usage
        recent_days = sorted(
            self.daily_usage.items(),
            key=lambda x: x[0],
            reverse=True
        )[:7]
        
        return {
            'total_api_calls': sum(self.daily_usage.values()),
            'daily_usage': dict(recent_days),
            'hourly_distribution': dict(self.hourly_usage),
            'top_endpoints': dict(top_endpoints),
            'peak_hours': dict(peak_hours),
            'unique_ips': len(self.ip_addresses),
            'unique_user_agents': len(self.user_agents)
        }


class AlertSystem:
    """Alert system for monitoring critical events"""
    
    def __init__(self):
        self.alerts = deque(maxlen=100)
        self.alert_rules = {
            'high_cpu': {'threshold': 80, 'enabled': True},
            'high_memory': {'threshold': 85, 'enabled': True},
            'high_error_rate': {'threshold': 15, 'enabled': True},
            'slow_response': {'threshold': 10, 'enabled': True}
        }
    
    def check_alerts(self, performance_monitor: PerformanceMonitor):
        """Check for alert conditions"""
        stats = performance_monitor.get_performance_stats()
        alerts_triggered = []
        
        # Check CPU usage
        if (self.alert_rules['high_cpu']['enabled'] and 
            stats['system'].get('cpu_percent', 0) > self.alert_rules['high_cpu']['threshold']):
            alert = self.create_alert(
                'high_cpu',
                f"CPU usage is {stats['system']['cpu_percent']}%",
                'warning'
            )
            alerts_triggered.append(alert)
        
        # Check memory usage
        if (self.alert_rules['high_memory']['enabled'] and 
            stats['system'].get('memory_percent', 0) > self.alert_rules['high_memory']['threshold']):
            alert = self.create_alert(
                'high_memory',
                f"Memory usage is {stats['system']['memory_percent']}%",
                'warning'
            )
            alerts_triggered.append(alert)
        
        # Check error rate
        if (self.alert_rules['high_error_rate']['enabled'] and 
            stats['error_rate'] > self.alert_rules['high_error_rate']['threshold']):
            alert = self.create_alert(
                'high_error_rate',
                f"Error rate is {stats['error_rate']}%",
                'critical'
            )
            alerts_triggered.append(alert)
        
        # Check response times
        if (self.alert_rules['slow_response']['enabled'] and 
            stats['response_times']['average'] > self.alert_rules['slow_response']['threshold']):
            alert = self.create_alert(
                'slow_response',
                f"Average response time is {stats['response_times']['average']}s",
                'warning'
            )
            alerts_triggered.append(alert)
        
        return alerts_triggered
    
    def create_alert(self, alert_type: str, message: str, severity: str) -> Dict:
        """Create a new alert"""
        alert = {
            'id': len(self.alerts) + 1,
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'resolved': False
        }
        
        self.alerts.append(alert)
        logger.warning(f"Alert triggered: {message}")
        
        return alert
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all active alerts"""
        return [alert for alert in self.alerts if not alert['resolved']]
    
    def resolve_alert(self, alert_id: int) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['resolved'] = True
                return True
        return False


# Global instances
performance_monitor = PerformanceMonitor()
api_analytics = APIAnalytics()
alert_system = AlertSystem()


def create_monitoring_middleware(app):
    """Create Flask middleware for performance monitoring"""
    
    @app.before_request
    def before_request():
        """Record request start"""
        from flask import request, g
        
        performance_monitor.start_request()
        
        # Record analytics
        api_analytics.record_api_call(
            endpoint=request.endpoint or request.path,
            user_agent=request.headers.get('User-Agent', ''),
            ip_address=request.remote_addr or ''
        )
    
    @app.after_request
    def after_request(response):
        """Record request completion"""
        from flask import request, g
        
        performance_monitor.end_request()
        
        # Calculate request duration
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            performance_monitor.record_request(
                endpoint=request.endpoint or request.path,
                method=request.method,
                duration=duration,
                status_code=response.status_code
            )
        
        return response
    
    @app.before_request
    def set_start_time():
        """Set request start time"""
        from flask import g
        g.start_time = time.time()
    
    return app
