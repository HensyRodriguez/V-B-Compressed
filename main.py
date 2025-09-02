import os # POSIX commands
import subprocess # For running ffmpeg

import customtkinter as ctk
from customtkinter import filedialog

class Video_Compressor:
    def __init__(self):
        # Set the window component.
        self.window = ctk.CTk()
        self.window.title('VBCOMPRESSED')
        self.window.geometry('640')
        self.window.resizable(False, False)
        self.window.eval('tk::PlaceWindow . center') # Makes window pop up on screen center

        # Adjusts window padding
        self.padding: dict = {'padx':20, 'pady':10}

        """ENTRY is where user can input"""
        # GUI for INPUT label and entry
        self.input_label = ctk.CTkLabel(self.window, text='Video to Compress-->')
        self.input_label.grid(row=0, column=0, **self.padding)
        self.input_label_entry = ctk.CTkEntry(self.window)
        self.input_label_entry.grid(row=0, column=1, **self.padding)

        # GUI for OUTPUT label and entry
        self.output_label = ctk.CTkLabel(self.window, text='Place to Output-->')
        self.output_label.grid(row=0, column=2, **self.padding)
        self.output_label_entry = ctk.CTkEntry(self.window)
        self.output_label_entry.grid(row=0, column=3, **self.padding)

        # Select File Button
        self.select_file_button = ctk.CTkButton(self.window, text='Select File to Compress', command=self.input_select_file)
        self.select_file_button.grid(row=1, column=1, **self.padding)

        # Select Output Button
        self.select_output_directory_button = ctk.CTkButton(self.window, text='Select Output Directory', command=self.select_directory_output)
        self.select_output_directory_button.grid(row=1, column=3, **self.padding)

        # Compress File button
        self.compress_video_button = ctk.CTkButton(self.window, text='Compress Video', command=self.run_compressor)
        self.compress_video_button.grid(row=0, column=4, **self.padding)

        # Size Slider Label
        self.size_slider_label = ctk.CTkLabel(self.window, text="Target File Size %:")
        self.size_slider_label.grid(row=2, column=0, **self.padding)

        # Size Slider
        self.size_slider = ctk.CTkSlider(self.window, from_=10, to=100, number_of_steps=90)
        self.size_slider.set(70)  # Default value 70%
        self.size_slider.grid(row=2, column=1, columnspan=3, sticky="ew", **self.padding)

        # Show the selected % dynamically
        self.slider_value_label = ctk.CTkLabel(self.window, text="70%")
        self.slider_value_label.grid(row=2, column=4, **self.padding)

        # Update the slider value text dynamically
        self.size_slider.configure(command=lambda value: self.slider_value_label.configure(text=f"{int(value)}%"))

    def input_select_file(self):
        self.selected_file = ctk.filedialog.askopenfilename()

        self.input_label_entry.delete(0, ctk.END) # Clears everything in input_label_entry
        self.input_label_entry.insert(0, self.selected_file)

    def select_directory_output(self):
        self.selected_directory = ctk.filedialog.askdirectory()

        self.output_label_entry.delete(0, ctk.END) # Clears everything in output_label_entry
        self.output_label_entry.insert(0, self.selected_directory)

    def get_video_duration(self, filepath: str) -> float:
        # Use ffprobe to get video duration in seconds
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                filepath
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return float(result.stdout.strip())

    def compress_video(self, video_to_compress: str):
        output_directory = self.output_label_entry.get()
        if not output_directory:
            output_directory = os.path.dirname(video_to_compress)
        
        original_filename = os.path.splitext(os.path.basename(video_to_compress))[0]
        output_file = os.path.join(output_directory, f"{original_filename}_compressed.mp4")

        # Get file size and duration
        original_size_bytes = os.path.getsize(video_to_compress)
        original_size_bits = original_size_bytes * 8
        duration_seconds = self.get_video_duration(video_to_compress)

        # Get target % from slider
        target_percent = self.size_slider.get()
        target_size_bits = original_size_bits * (target_percent / 100)

        # Calculate needed bitrate
        target_bitrate = target_size_bits / duration_seconds  # bits/sec

        # Convert bitrate to kilobits/sec for ffmpeg (-b:v expects kbps)
        target_bitrate_kbps = int(target_bitrate / 1000)

        print(f"Original Size: {original_size_bytes} bytes")
        print(f"Duration: {duration_seconds} seconds")
        print(f"Target %: {target_percent}%")
        print(f"Target Bitrate: {target_bitrate_kbps} kbps")

        # Run ffmpeg command with flags
        subprocess.run([
            "ffmpeg", "-y", "-i", video_to_compress,
            "-b:v", f"{target_bitrate_kbps}k",
            "-preset", "slow",
            "-movflags", "+faststart",
            "-acodec", "aac",
            output_file
        ])

    def run_compressor(self):
        if os.path.exists(self.input_label_entry.get()):
            self.compress_video(self.input_label_entry.get())
            self.compress_video_button.configure(text="VIDEO COMPRESSED!")

            # After 1000 milliseconds (1 second), reset button text back to normal
            self.window.after(1000, lambda: self.compress_video_button.configure(text="Compress Video"))
        else:
            self.input_label_entry.delete(0, ctk.END)
            self.input_label_entry.insert(0, "INVALID FILE!")

    def run(self):
        self.window.mainloop() # Main window loop


if __name__ == "__main__":
    # ffmpeg -i input.mp4 -vcodec libx265 -crf 28 output.mp4
    video_compressor = Video_Compressor()
    video_compressor.run()
    
