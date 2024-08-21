import PyPDF2
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import textwrap

# 1. Extract Text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

# 2. Simple Summarization
def summarize_text(pdf_text):
    # Simple summarization: just take the first 1000 characters
    short_summary = pdf_text[:1000]
    
    # Create a short summary by picking the first 200 characters for demonstration
    spacy_summary = short_summary[:200]
    return spacy_summary, short_summary

# 3. Generate Narration
def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)

# 4. Create Visual Slides
def create_slide(text, output_path):
    width, height = 800, 600
    image = Image.new("RGB", (width, height), "lightblue")  # Background color
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 24)  # Font size
    
    # Handle text wrapping
    wrapped_text = textwrap.fill(text, width=30)
    
    # Determine text size and position
    try:
        # Use textbbox for text size calculation
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except AttributeError:
        # Fallback to textlength and font.getsize() if textbbox is not available
        text_w = draw.textlength(wrapped_text, font=font)
        text_h = font.getsize(wrapped_text)[1]
    
    # Draw text
    draw.text(((width - text_w) / 2, (height - text_h) / 2), wrapped_text, font=font, fill="black")
    
    image.save(output_path)

# 5. Chunk Text
def chunk_text(text, chunk_size=200):
    return textwrap.wrap(text, chunk_size)

# 6. Assemble the Video
def create_video(slide_images, audio_file, output_video):
    clips = [ImageClip(img).set_duration(5) for img in slide_images]
    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(audio_file)
    video = video.set_audio(audio)
    video.write_videofile(output_video, fps=24)

# 7. Adding Transitions
def add_transitions(clips):
    return [clip.crossfadein(1) for clip in clips]

# Main execution
if __name__ == "__main__":
    pdf_text = extract_text_from_pdf('sample.pdf')
    spacy_summary, short_summary = summarize_text(pdf_text)
    
    text_to_speech(short_summary, 'narration.mp3')
    
    # Generate slides based on summaries
    create_slide(spacy_summary, "slide1.jpg")
    
    # Chunk the summary and generate slides for each chunk
    chunks = chunk_text(short_summary, chunk_size=200)  # Adjust chunk_size as needed
    image_paths = []
    
    for i, chunk in enumerate(chunks):
        image_path = f"slide_{i + 2}.jpg"
        create_slide(chunk, image_path)
        image_paths.append(image_path)
    
    clips = [ImageClip(img).set_duration(5) for img in ["slide1.jpg"] + image_paths]
    clips = add_transitions(clips)
    
    final_video = concatenate_videoclips(clips, method="compose")
    final_video.set_audio(AudioFileClip("narration.mp3"))
    final_video.write_videofile("final_output.mp4", fps=24)
