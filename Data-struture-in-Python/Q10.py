from collections import deque

class BrowserHistory:
    def __init__(self, max_size=5):
        self.history = deque(maxlen=max_size)
        self.forward_stack = deque()

    def add_page(self, url):
        self.history.append(url)
        self.forward_stack.clear() 
        self.display_state(f"Visited: {url}")

    def go_back(self):
        if len(self.history) > 1:
            last_page = self.history.pop()
            self.forward_stack.append(last_page)
            self.display_state(f"Went back from: {last_page}")
        else:
            print("Cannot go back. No previous page.")
            self.display_state()

    def go_forward(self):
        if self.forward_stack:
            page = self.forward_stack.pop()
            self.history.append(page)
            self.display_state(f"Went forward to: {page}")
        else:
            print("Cannot go forward. Forward stack is empty.")
            self.display_state()

    def display_state(self, action=None):
        if action:
            print(f"\nAction: {action}")
        print(f"Current history: {list(self.history)}")
        print(f"Forward stack: {list(self.forward_stack)}\n")

bh = BrowserHistory(max_size=5)
bh.add_page("google.com")
bh.add_page("openai.com")
bh.add_page("github.com")
bh.add_page("wikipedia.org")
bh.add_page("stackoverflow.com")
bh.add_page("python.org")  
bh.go_back()
bh.go_back()
bh.go_forward()
bh.add_page("reddit.com") 
