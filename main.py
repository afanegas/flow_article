# main.py
import requests
import sys
import json
import subprocess

def check_article(word: str) -> str:
    """
    Überprüft den deutschen Artikel für ein Wort auf der-artikel.de
    """
    base_url = "https://der-artikel.de"
    articles = ["der", "die", "das"]
    
    for article in articles:
        url = f"{base_url}/{article}/{word.capitalize()}.html"
        try:
            response = requests.head(url, allow_redirects=True, timeout=3)
            if response.status_code == 200:
                return f"{article} {word}"
        except requests.RequestException:
            continue
    
    return None

def copy_to_clipboard(text: str):
    """
    Kopiert Text in die Zwischenablage
    """
    try:
        subprocess.run(['clip'], input=text.encode('utf-8'), check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        return False

def query(word: str):
    """
    Query-Funktion für Flow Launcher
    """
    results = []
    
    if not word or len(word.strip()) == 0:
        results.append({
            "Title": "Der Artikel",
            "SubTitle": "Gib ein deutsches Wort ein um den Artikel zu finden",
            "IcoPath": "icon.png"
        })
    else:
        words = word.strip().split()
        
        for w in words:
            if len(w) < 2:  # Zu kurze Wörter ignorieren
                continue
                
            result = check_article(w)
            
            if result:
                results.append({
                    "Title": f"> {result}",
                    "SubTitle": f"Artikel gefunden! Enter zum Kopieren",
                    "IcoPath": "icon.png",
                    "JsonRPCAction": {
                        "method": "copy_result",
                        "parameters": [result]
                    }
                })
            else:
                results.append({
                    "Title": f"[X] Kein Artikel für: {w}",
                    "SubTitle": "Wort nicht in der Datenbank gefunden",
                    "IcoPath": "icon.png"
                })
    
    return json.dumps({"result": results}, ensure_ascii=True)

def copy_result(text: str):
    """
    Kopiert Ergebnis in die Zwischenablage
    """
    success = copy_to_clipboard(text)
    return json.dumps({"result": []}, ensure_ascii=True)

def main():
    """
    Hauptfunktion für Flow Launcher
    """
    try:
        if len(sys.argv) < 2:
            print(json.dumps({"result": []}, ensure_ascii=True))
            return
        
        # Flow Launcher übergibt JSON als Argument
        request_data = sys.argv[1]
        request = json.loads(request_data)
        
        method = request.get('method', '')
        parameters = request.get('parameters', [])
        
        if method == 'query':
            query_text = parameters[0] if parameters else ""
            result = query(query_text)
            print(result)
            
        elif method == 'copy_result':
            text = parameters[0] if parameters else ""
            result = copy_result(text)
            print(result)
            
        else:
            print(json.dumps({"result": []}, ensure_ascii=True))
            
    except Exception as e:
        # Fehlerbehandlung
        error_response = {
            "result": [{
                "Title": f"Plugin Fehler: {str(e)[:50]}",
                "SubTitle": "Bitte versuche es erneut oder kontaktiere den Entwickler",
                "IcoPath": "icon.png"
            }]
        }
        print(json.dumps(error_response, ensure_ascii=True))

if __name__ == "__main__":
    main()