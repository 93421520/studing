class StudyLogic:
    def __init__(self, db):
        self.db = db

    def submit_task(self, task_id):
        self.db.cursor.execute("UPDATE tasks SET status=1 WHERE id=?", (task_id,))
        self.db.conn.commit()

    def approve_task(self, task_id, quality):
        multipliers = {"luxury": 1.5, "standard": 1.0, "basic": 0.5}
        self.db.cursor.execute("SELECT child_id, points FROM tasks WHERE id=?", (task_id,))
        cid, base_pts = self.db.cursor.fetchone()
        final_pts = int(base_pts * multipliers.get(quality, 1.0))
        self.db.cursor.execute("UPDATE tasks SET status=2, quality=? WHERE id=?", (quality, task_id))
        self.db.cursor.execute("UPDATE wallet SET points = points + ? WHERE child_id=?", (final_pts, cid))
        self.db.conn.commit()
        return final_pts