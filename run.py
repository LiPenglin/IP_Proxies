from proxy.schedule import Schedule
from proxy.api import app

def main():
    s = Schedule()
    s.run()
    app.run()

if __name__ == '__main__':
    main()
