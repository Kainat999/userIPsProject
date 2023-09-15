# middleware.py
import logging
import time

logger = logging.getLogger(__name__)

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.blocked_ips = {}
        self.blocked_duration = 60  # 1 minute

    def __call__(self, request):
        user_ip = self.get_client_ip(request)
        logger.info(f"User IP: {user_ip}, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        if request.user.is_authenticated:
            group = request.user.groups.first()
            if group:
                group_name = group.name
                max_requests = {
                    'Gold': 10,
                    'Silver': 7,
                    'Bronze': 5,
                }.get(group_name, 1)
                if self.is_blocked(user_ip, max_requests):
                    raise Exception("User blocked due to excessive requests. Try again later.")

        response = self.get_response(request)
        return response  

            

    def is_blocked(self, ip, max_requests):
        current_time = int(time.time())
        if ip not in self.blocked_ips:
            self.blocked_ips[ip] = [current_time]
            return False

        requests = self.blocked_ips[ip]
        while requests and requests[0] <= current_time - self.blocked_duration:
            requests.pop(0)

        if len(requests) < max_requests:
            requests.append(current_time)
            return False

        return True

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
