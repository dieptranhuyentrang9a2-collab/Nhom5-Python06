from datetime import datetime
 
 
class ActivityLog:
    def __init__(self, storage):
        self._storage = storage
 
    def write(self, user, action):
        logs = self._storage.load() or []
        logs.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user,
            "action": action,
        })
        self._storage.save(logs)
 
    def get_all(self):
        return self._storage.load() or []
