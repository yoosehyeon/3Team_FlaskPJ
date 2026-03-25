# apscheduler=3.x
# 실시간 데이터 갱신을 위해 향후 확장 포인트를 잡아둠
import logging

def start_scheduler():
    logging.info("Scheduler disabled for v3.0 logic.")
    # from apscheduler.schedulers.background import BackgroundScheduler
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(fetch_elevators_job, 'interval', minutes=10)
    # scheduler.start()

if __name__ == "__main__":
    start_scheduler()
