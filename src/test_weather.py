from cursor_mcp import get_weather

def main():
    location = "서울"
    weather = get_weather(location)
    print(f"{location}의 날씨: {weather}")

if __name__ == "__main__":
    main() 