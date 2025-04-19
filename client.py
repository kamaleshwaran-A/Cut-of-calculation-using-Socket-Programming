import tkinter as tk
from tkinter import messagebox, ttk
import asyncio
import websockets
import json

class CutoffCalculatorClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Cutoff Calculator Client")
        self.center_window(450, 500)

        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        self.label_scheme = tk.Label(main_frame, text="Select Scheme", font=("Arial", 14, "bold"))
        self.label_scheme.grid(row=0, column=0, pady=10)

        self.scheme_var = tk.StringVar()
        self.scheme_dropdown = ttk.Combobox(main_frame, textvariable=self.scheme_var, font=("Arial", 12), state="readonly")
        self.scheme_dropdown['values'] = ("Agri", "Engineering", "TNPSC", "UPSC", "CAT")
        self.scheme_dropdown.grid(row=0, column=1, padx=10)
        self.scheme_dropdown.bind("<<ComboboxSelected>>", self.update_fields)

        self.input_frame = tk.Frame(main_frame)
        self.input_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.entries = {}
        self.create_input_field("Physics")
        self.create_input_field("Chemistry")
        self.create_input_field("Biology", hide=True)
        self.create_input_field("Maths", hide=True)
        self.create_input_field("Candidate Marks", hide=True)
        self.create_input_field("GS Paper I Marks", hide=True)
        self.create_input_field("Mains Marks", hide=True)
        self.create_input_field("Interview Marks", hide=True)
        self.create_input_field("CAT Score", hide=True)
        self.create_input_field("Total Candidates", hide=True)
        self.create_input_field("Candidates Scored Below", hide=True)

        self.calculate_button = tk.Button(main_frame, text="Calculate Cutoff", command=self.calculate_cutoff, font=("Arial", 14), bg="#4CAF50", fg="white")
        self.calculate_button.grid(row=2, column=0, columnspan=2, pady=20, ipadx=10)

        self.result_label = tk.Label(main_frame, text="", font=("Arial", 12, "bold"), fg="blue")
        self.result_label.grid(row=3, column=0, columnspan=2, pady=10)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_input_field(self, label_text, hide=False):
        label = tk.Label(self.input_frame, text=f"{label_text}:", font=("Arial", 12, "bold"))
        entry = tk.Entry(self.input_frame, font=("Arial", 12), width=10)
        if hide:
            label.grid_remove()
            entry.grid_remove()
        else:
            label.grid(sticky="e", padx=5, pady=5)
            entry.grid(row=label.grid_info()["row"], column=1, padx=5, pady=5)
        self.entries[label_text] = (label, entry)

    def update_fields(self, event=None):
        scheme = self.scheme_var.get()
        for label, entry in self.entries.values():
            label.grid_remove()
            entry.grid_remove()
        if scheme == "Agri":
            for field in ["Physics", "Chemistry", "Biology"]:
                self.entries[field][0].grid()
                self.entries[field][1].grid()
        elif scheme == "Engineering":
            for field in ["Physics", "Chemistry", "Maths"]:
                self.entries[field][0].grid()
                self.entries[field][1].grid()
        elif scheme == "TNPSC":
            self.entries["Candidate Marks"][0].grid()
            self.entries["Candidate Marks"][1].grid()
        elif scheme == "UPSC":
            self.entries["GS Paper I Marks"][0].grid()
            self.entries["GS Paper I Marks"][1].grid()
            self.entries["Mains Marks"][0].grid()
            self.entries["Mains Marks"][1].grid()
            self.entries["Interview Marks"][0].grid()
            self.entries["Interview Marks"][1].grid()
        elif scheme == "CAT":
            for field in ["CAT Score", "Total Candidates", "Candidates Scored Below"]:
                self.entries[field][0].grid()
                self.entries[field][1].grid()

    async def send_calculation_request(self, data):
        uri = "ws://localhost:6789"
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(data))
            response = await websocket.recv()
            return json.loads(response)

    def calculate_cutoff(self):
        scheme = self.scheme_var.get()
        if not scheme:
            messagebox.showwarning("Input Error", "Please select a scheme.")
            return
        data = {"scheme": scheme}
        try:
            for key in self.entries:
                if self.entries[key][1].winfo_ismapped():
                    data[key.lower().replace(" ", "_")] = float(self.entries[key][1].get())

            asyncio.run(self.async_calculate_cutoff(data))

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for marks.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the server: {str(e)}")

    async def async_calculate_cutoff(self, data):
        result = await self.send_calculation_request(data)
        if "cutoff" in result:
            self.result_label.config(text=f"Calculated Cutoff: {result['cutoff']}")
        else:
            self.result_label.config(text=f"Error: {result['error']}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CutoffCalculatorClient(root)
    root.mainloop()
