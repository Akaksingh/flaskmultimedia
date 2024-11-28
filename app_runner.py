import subprocess

def run_user_service():
    subprocess.Popen(["D:\\akaksha\\social_media_app\\venv\\Scripts\\python", "user_app/app.py"])

def run_post_service():
    subprocess.Popen(["D:\\akaksha\\social_media_app\\venv\\Scripts\\python", "post_app/app.py"])

if __name__ == '__main__':
    run_user_service()
    run_post_service()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nTerminating both the processes. Alvida!")
