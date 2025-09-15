# """
# AI Question Generator with Image Analysis
# Main Streamlit Application - Fixed Version
# """

# import streamlit as st
# import time
# import re
# from question_generator import QuestionGenerator, get_openai_api_key
# from image_processor import ImageProcessor

# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
# from reportlab.lib.styles import getSampleStyleSheet
# from io import BytesIO


# # Initialize session state
# if 'generated_question_sets' not in st.session_state:
#     st.session_state.generated_question_sets = []
# if 'current_set' not in st.session_state:
#     st.session_state.current_set = 0
# if 'extracted_images' not in st.session_state:
#     st.session_state.extracted_images = []

# def display_question_set_with_images(set_data, image_analyses):
#     """Display questions with embedded images"""
#     questions_text = set_data['questions']
    
#     # Split questions for processing
#     question_blocks = questions_text.split('\n\nQ')
#     if question_blocks:
#         # Handle first question (doesn't have \n\n prefix)
#         if question_blocks[0].startswith('Q'):
#             first_q = question_blocks[0]
#         else:
#             first_q = 'Q' + question_blocks[0] if question_blocks[0] else ''
        
#         # Handle remaining questions
#         other_qs = ['Q' + block for block in question_blocks[1:] if block.strip()]
        
#         all_questions = [first_q] + other_qs if first_q.strip() else other_qs
#     else:
#         all_questions = [questions_text]
    
#     for i, question in enumerate(all_questions):
#         if not question.strip():
#             continue
            
#         st.markdown(f"### Question {i+1}")
        
#         # Check for image references in this question
#         image_pattern = r'\[IMAGE:img_(\d+)\]'
#         matches = re.findall(image_pattern, question)
        
#         if matches:
#             # Display images first, then question
#             for match in matches:
#                 img_num = int(match) - 1
#                 if 0 <= img_num < len(image_analyses):
#                     col1, col2 = st.columns([1, 2])
#                     with col1:
#                         st.image(
#                             image_analyses[img_num]['image'], 
#                             caption=f"Image {img_num + 1}: {image_analyses[img_num]['source']}",
#                             width=300
#                         )
#                     with col2:
#                         # Remove image reference from question text and display
#                         clean_question = re.sub(image_pattern, '', question).strip()
#                         st.markdown(clean_question)
#         else:
#             # Display question without image
#             st.markdown(question)
        
#         st.markdown("---")

# def main():
#     st.set_page_config(
#         page_title="AI Question Generator with Image Analysis",
#         page_icon="📝",
#         layout="wide"
#     )
    
#     st.title("🎓 AI Question Generator with Image Display")
#     st.markdown("Upload documents and generate **5 different question sets** with questions about text AND images shown in questions!")
    
#     # Check API key
#     api_key = get_openai_api_key()
#     if not api_key:
#         st.error("❌ OpenAI API key not found!")
#         st.markdown("""
#         **Setup Instructions:**
#         1. Create a `.env` file in your project folder
#         2. Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`
#         3. Or add it to Streamlit secrets if deploying to cloud
        
#         Get your API key from: https://platform.openai.com/account/api-keys
#         """)
#         st.stop()
    
#     qg = QuestionGenerator()
    
#     with st.sidebar:
#         st.header("⚙️ Settings")
#         st.success("✅ API Key Loaded")
#         st.info("🖼️ Image Display Enabled")
        
#         # Debug information
#         st.subheader("🐛 Debug Info")
#         if st.button("Show API Key Status"):
#             if api_key:
#                 st.success(f"✅ API Key loaded (starts with: {api_key[:10]}...)")
#             else:
#                 st.error("❌ No API Key found")
        
#         if st.button("🗑️ Clear All Data"):
#             st.session_state.generated_question_sets = []
#             st.session_state.current_set = 0
#             st.session_state.extracted_images = []
#             st.rerun()
        
#         # Question Set Navigation
#         if st.session_state.generated_question_sets:
#             st.subheader("📚 Generated Sets")
#             set_options = [f"Set {i+1}" for i in range(len(st.session_state.generated_question_sets))]
#             selected_set = st.selectbox("Choose Set to View:", set_options, index=st.session_state.current_set)
#             st.session_state.current_set = set_options.index(selected_set)
        
#         # Show extracted images
#         if st.session_state.extracted_images:
#             st.subheader("🖼️ Extracted Images")
#             st.write(f"Found {len(st.session_state.extracted_images)} images")
#             if st.button("👁️ Show Image Preview"):
#                 for i, img_data in enumerate(st.session_state.extracted_images[:3]):  # Show first 3
#                     st.image(img_data['image'], caption=f"Image {i+1}: {img_data['source']}", width=200)
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         st.header("📄 Upload Study Materials")
#         uploaded_files = st.file_uploader(
#             "Choose PDF, DOCX, or TXT files (max 2)",
#             type=['pdf', 'docx', 'txt'],
#             accept_multiple_files=True,
#             help="Upload your study materials (PDFs and DOCX files will be scanned for images)"
#         )
        
#         if uploaded_files and len(uploaded_files) > 2:
#             st.warning("Maximum 2 files allowed")
#             uploaded_files = uploaded_files[:2]
        
#         st.header("📄 (Optional) Reference Question Paper")
#         ref_file = st.file_uploader(
#             "Upload reference paper (PDF, DOCX, or TXT)",
#             type=['pdf', 'docx', 'txt'],
#             accept_multiple_files=False,
#             help="Upload a sample question paper to match the style (images will also be extracted)"
#         )
        
#         st.header("🔗 Web Links (Optional)")
#         url1 = st.text_input("URL 1", placeholder="https://example.com/article")
#         url2 = st.text_input("URL 2", placeholder="https://example.com/resource")
        
#         st.header("⚙️ Question Settings")
#         col_set1, col_set2 = st.columns(2)
        
#         with col_set1:
#             difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
        
#         with col_set2:
#             num_questions = st.slider("Questions per Set", 5, 25, 12, 1)
        
#         question_types = st.multiselect(
#             "Select Question Types",
#             ["Multiple Choice Questions (MCQ)", "Short Answer", "Long Answer", "Fill in the Blanks", "True/False"],
#             default=["Multiple Choice Questions (MCQ)", "Short Answer"],
#             help="Choose the types of questions you want to generate"
#         )
        
#         # Generate button
#         generate_disabled = not uploaded_files and not url1.strip() and not url2.strip()
        
#         # Info box about image feature
#         st.info("🎯 **New Image Feature**: Images will be displayed directly in questions! Questions will show relevant images above the question text.")
        
#         if st.button("🚀 Generate 5 Question Sets with Images", type="primary", use_container_width=True, disabled=generate_disabled):
#             if generate_disabled:
#                 st.error("❌ Please upload at least one file or provide a URL")
#             else:
#                 # Show processing status
#                 with st.container():
#                     st.subheader("📋 Processing Status")
                    
#                     # Progress tracking
#                     progress_placeholder = st.empty()
#                     status_placeholder = st.empty()
                    
#                     all_content = ""
#                     total_sources = len([f for f in uploaded_files if f] if uploaded_files else [])
#                     total_sources += len([u for u in [url1, url2] if u.strip()])
                    
#                     processed = 0
                    
#                     # Process uploaded files
#                     if uploaded_files:
#                         for file in uploaded_files:
#                             status_placeholder.info(f"Processing {file.name}...")
                            
#                             if file.type == "application/pdf":
#                                 text = qg.extract_text_from_pdf(file)
#                             elif "wordprocessingml" in file.type:
#                                 text = qg.extract_text_from_docx(file)
#                             elif file.type == "text/plain":
#                                 text = qg.extract_text_from_txt(file)
#                             else:
#                                 st.warning(f"⚠️ Unsupported file type: {file.type}")
#                                 text = ""
                            
#                             if text.strip():
#                                 all_content += f"\n\n=== Content from {file.name} ===\n{text}"
                            
#                             processed += 1
#                             progress_placeholder.progress(processed / total_sources)
                    
#                     # Process URLs
#                     for i, url in enumerate([url1, url2], 1):
#                         if url.strip():
#                             status_placeholder.info(f"Processing URL {i}...")
#                             text = qg.extract_text_from_url(url.strip())
                            
#                             if text.strip():
#                                 all_content += f"\n\n=== Content from URL {i} ===\n{text}"
                            
#                             processed += 1
#                             progress_placeholder.progress(processed / total_sources)
                    
#                     # Process reference file
#                     reference_style = ""
#                     if ref_file:
#                         status_placeholder.info("Processing reference paper...")
                        
#                         if ref_file.type == "application/pdf":
#                             reference_style = qg.extract_text_from_pdf(ref_file)
#                         elif "wordprocessingml" in ref_file.type:
#                             reference_style = qg.extract_text_from_docx(ref_file)
#                         elif ref_file.type == "text/plain":
#                             reference_style = qg.extract_text_from_txt(ref_file)
                        
#                         if reference_style.strip():
#                             st.info("📄 Reference paper style will be used for question formatting.")
                    
#                     # Clear initial progress indicators
#                     progress_placeholder.empty()
#                     status_placeholder.empty()
                    
#                     # Process images from all sources - FIXED BUG HERE
#                     st.subheader("🖼️ Image Processing")
#                     urls_list = [url for url in [url1, url2] if url.strip()]
                    
#                     # FIX: Handle ref_file properly - ensure it's passed as expected
#                     ref_files_list = []
#                     if ref_file is not None:
#                         # ref_file should be a single file object from st.file_uploader
#                         if hasattr(ref_file, 'type'):  # Valid file object
#                             ref_files_list = [ref_file]  # Wrap in list for consistency
#                         else:
#                             st.warning(f"⚠️ Reference file has unexpected format: {type(ref_file)}")
                    
#                     # Pass the processed ref_files_list instead of ref_file directly
#                     image_analyses = qg.image_processor.process_all_images(uploaded_files, urls_list, ref_files_list)
                    
#                     # Store in session state for display
#                     st.session_state.extracted_images = image_analyses
                    
#                     # Check if we have content
#                     if all_content.strip() or image_analyses:
#                         if all_content.strip():
#                             st.success(f"✅ Successfully extracted {len(all_content)} characters from all sources")
#                         if image_analyses:
#                             st.success(f"✅ Successfully analyzed {len(image_analyses)} images")
                        
#                         # Generate multiple question sets
#                         st.subheader("🎯 Generating 5 Unique Question Sets")
#                         question_sets = qg.generate_multiple_question_sets(
#                             all_content, difficulty, num_questions, question_types, reference_style, image_analyses, 5
#                         )
                        
#                         if question_sets:
#                             st.session_state.generated_question_sets = question_sets
#                             st.session_state.current_set = 0
#                             st.success(f"🎉 Generated {len(question_sets)} question sets successfully!")
#                             st.balloons()
#                         else:
#                             st.error("❌ Failed to generate question sets. Please try again.")
#                     else:
#                         st.error("❌ No content or images could be extracted from any source. Please check your files and URLs.")
                        
#                         # Show debugging info
#                         st.subheader("🐛 Debug Information")
#                         st.write(f"Files uploaded: {len(uploaded_files) if uploaded_files else 0}")
#                         st.write(f"URLs provided: {len([u for u in [url1, url2] if u.strip()])}")
#                         st.write(f"Images found: {len(image_analyses)}")
                        
#                         if uploaded_files:
#                             for file in uploaded_files:
#                                 st.write(f"- {file.name}: {file.size} bytes, type: {file.type}")
    
#     with col2:
#         st.header("📊 Summary")
        
#         if uploaded_files:
#             st.subheader("📁 Files")
#             for file in uploaded_files:
#                 file_size = file.size / 1024  # Convert to KB
#                 st.write(f"• {file.name} ({file_size:.1f} KB)")
        
#         if ref_file:
#             st.subheader("📄 Reference Paper")
#             st.write(f"• {ref_file.name}")
        
#         urls = [url for url in [url1, url2] if url.strip()]
#         if urls:
#             st.subheader("🌐 URLs")
#             for i, url in enumerate(urls, 1):
#                 st.write(f"• URL {i}: {url[:30]}{'...' if len(url) > 30 else ''}")
        
#         st.subheader("⚙️ Settings")
#         if 'difficulty' in locals():
#             st.write(f"**Difficulty:** {difficulty}")
#             st.write(f"**Questions per Set:** {num_questions}")
#             st.write(f"**Total Sets:** 5")
#             st.write(f"**Total Questions:** {num_questions * 5}")
#             if 'question_types' in locals() and question_types:
#                 st.write(f"**Types:** {', '.join(question_types[:2])}{'...' if len(question_types) > 2 else ''}")
        
#         # Set variation info
#         if st.session_state.generated_question_sets:
#             st.subheader("🎯 Set Variations")
#             variations = [
#                 "Theoretical concepts",
#                 "Practical applications", 
#                 "Analytical problems",
#                 "Comparative analysis",
#                 "Higher-order thinking"
#             ]
#             for i, var in enumerate(variations):
#                 st.write(f"**Set {i+1}:** {var}")
        
#         # Image analysis summary
#         if st.session_state.extracted_images:
#             st.subheader("🖼️ Image Analysis")
#             st.write(f"**Images Found:** {len(st.session_state.extracted_images)}")
#             st.write("**Sources:**")
#             sources = set(img['source'] for img in st.session_state.extracted_images)
#             for source in list(sources)[:3]:
#                 st.write(f"• {source}")
#             if len(sources) > 3:
#                 st.write(f"• ... and {len(sources) - 3} more")
    
#     # Display results for selected set
#     if st.session_state.generated_question_sets:
#         current_set_data = st.session_state.generated_question_sets[st.session_state.current_set]
        
#         st.header(f"📝 Question Set {current_set_data['set_number']}")
        
#         # Download buttons for current set
#         col_d1, col_d2, col_d3 = st.columns(3)
        
#         with col_d1:
#             st.download_button(
#                 f"📄 Download Set {current_set_data['set_number']}",
#                 data=current_set_data['questions'],
#                 file_name=f"question_set_{current_set_data['set_number']}_{difficulty}_{int(time.time())}.txt",
#                 mime="text/plain"
#             )
        
        
#         with col_d2:
#             # Download all sets combined
#             all_sets_combined = ""
#             for i, set_data in enumerate(st.session_state.generated_question_sets):
#                 all_sets_combined += f"""
# {'='*60}
# QUESTION SET {set_data['set_number']}
# {'='*60}
# Generated: {set_data['timestamp']}

# {set_data['questions']}

# """
            
#             # Include image information in the header
#             image_info = ""
#             if st.session_state.extracted_images:
#                 image_info = f"""
# Images Analyzed: {len(st.session_state.extracted_images)}
# Image Sources: {', '.join(set(img['source'] for img in st.session_state.extracted_images))}
# """
            
#             formatted_all = f"""
# COMPLETE QUESTION BANK - ALL SETS (WITH IMAGE DISPLAY)
# ======================================================
# Difficulty: {difficulty if 'difficulty' in locals() else 'Medium'}
# Questions per Set: {num_questions if 'num_questions' in locals() else 10}
# Total Sets: {len(st.session_state.generated_question_sets)}
# Total Questions: {(num_questions if 'num_questions' in locals() else 10) * len(st.session_state.generated_question_sets)}
# Types: {', '.join(question_types) if 'question_types' in locals() and question_types else 'MCQ, Short Answer'}
# {image_info}
# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

# {all_sets_combined}
# """
            
#             st.download_button(
#                 "📦 Download All Sets",
#                 data=formatted_all,
#                 file_name=f"all_question_sets_with_images_{difficulty}_{int(time.time())}.txt",
#                 mime="text/plain"
#             )
        
#         with col_d3:
#             # Set navigation buttons
#             col_nav1, col_nav2 = st.columns(2)
#             with col_nav1:
#                 if st.button("⬅️ Previous", disabled=st.session_state.current_set == 0):
#                     st.session_state.current_set = max(0, st.session_state.current_set - 1)
#                     st.rerun()
#             with col_nav2:
#                 if st.button("Next ➡️", disabled=st.session_state.current_set >= len(st.session_state.generated_question_sets) - 1):
#                     st.session_state.current_set = min(len(st.session_state.generated_question_sets) - 1, st.session_state.current_set + 1)
#                     st.rerun()
        
#         # Show character count and image info
#         char_count = len(current_set_data['questions'])
#         image_count = len(st.session_state.extracted_images)
#         st.caption(f"Set {current_set_data['set_number']} - {char_count} characters - {image_count} images analyzed - Generated: {current_set_data['timestamp']}")
        
#         # Display current set questions with images
#         st.subheader(f"Questions - Set {current_set_data['set_number']}:")
        
#         # Toggle between formatted view and raw text
#         view_mode = st.radio(
#             "Display Mode:",
#             ["📖 Formatted View (with Images)", "📝 Raw Text"],
#             horizontal=True
#         )
        
#         if view_mode == "📖 Formatted View (with Images)":
#             if st.session_state.extracted_images:
#                 st.info("🖼️ Images will be displayed directly above related questions")
#             display_question_set_with_images(current_set_data, st.session_state.extracted_images)
#         else:
#             st.text_area(
#                 f"Raw Questions - Set {current_set_data['set_number']}:",
#                 value=current_set_data['questions'],
#                 height=400
#             )
        
#         # Show overview of all sets
#         if len(st.session_state.generated_question_sets) > 1:
#             with st.expander(f"📚 Overview of All {len(st.session_state.generated_question_sets)} Sets"):
#                 for i, set_data in enumerate(st.session_state.generated_question_sets):
#                     st.write(f"**Set {set_data['set_number']}** - {len(set_data['questions'])} characters - Generated: {set_data['timestamp']}")
        
#         # Show image analysis details
#         if st.session_state.extracted_images:
#             with st.expander(f"🖼️ Image Analysis Details ({len(st.session_state.extracted_images)} images)"):
#                 for i, img_data in enumerate(st.session_state.extracted_images):
#                     st.write(f"**Image {i+1}:** {img_data['source']}")
#                     with st.expander(f"View Image {i+1} & Analysis"):
#                         col_img1, col_img2 = st.columns([1, 2])
#                         with col_img1:
#                             st.image(img_data['image'], caption=f"Image {i+1}", width=200)
#                         with col_img2:
#                             st.write("**AI Analysis:**")
#                             st.write(img_data['analysis'][:500] + "..." if len(img_data['analysis']) > 500 else img_data['analysis'])

# if __name__ == "__main__":
#     main()


"""
AI Question Generator with Image Analysis
Main Streamlit Application - Fixed Version with PDF Download Support
"""

import streamlit as st
import time
import re
from question_generator import QuestionGenerator, get_openai_api_key
from image_processor import ImageProcessor

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from PIL import Image
import io
import base64



# Initialize session state
if 'generated_question_sets' not in st.session_state:
    st.session_state.generated_question_sets = []
if 'current_set' not in st.session_state:
    st.session_state.current_set = 0
if 'extracted_images' not in st.session_state:
    st.session_state.extracted_images = []

def generate_pdf_with_images(question_set_data, image_analyses, title="Question Set"):
    """Generate PDF with embedded images"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.black
    )
    
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        leftIndent=0
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        textColor=colors.darkblue
    )
    
    # Add title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))
    
    # Process questions text
    questions_text = question_set_data['questions']
    
    # Split by sections
    sections = re.split(r'(Section [AB]:.*?)\n', questions_text)
    
    current_section = ""
    for section in sections:
        if not section.strip():
            continue
            
        # Check if this is a section header
        if section.startswith('Section'):
            current_section = section
            elements.append(Paragraph(f"<b>{section}</b>", header_style))
            elements.append(Spacer(1, 12))
            continue
            
        # Process questions in this section
        lines = section.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line == "---":
                continue
                
            # Check for image references
            image_pattern = r'\[IMAGE:img_(\d+)\]'
            image_matches = re.findall(image_pattern, line)
            
            if image_matches:
                # Add images first
                for match in image_matches:
                    img_num = int(match) - 1
                    if 0 <= img_num < len(image_analyses):
                        try:
                            # Convert PIL image to ReportLab Image
                            img_data = image_analyses[img_num]['image']
                            img_buffer = io.BytesIO()
                            
                            # Resize image if too large
                            max_width, max_height = 400, 300
                            if img_data.width > max_width or img_data.height > max_height:
                                img_data.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                            
                            img_data.save(img_buffer, format='PNG')
                            img_buffer.seek(0)
                            
                            # Use BytesIO instead of temporary files
                            img_buffer.seek(0)
                            
                            # Create ReportLab Image directly from BytesIO
                            rl_image = RLImage(img_buffer, width=img_data.width, height=img_data.height)
                            elements.append(rl_image)
                            elements.append(Spacer(1, 12))
                            
                            # Add image caption
                            caption = f"Image {img_num + 1}: {image_analyses[img_num]['source']}"
                            elements.append(Paragraph(f"<i>{caption}</i>", styles['Normal']))
                            elements.append(Spacer(1, 12))
                        except Exception as e:
                            st.warning(f"Could not embed image {img_num + 1}: {str(e)}")
                
                # Remove image references from text and add question
                clean_line = re.sub(image_pattern, '', line).strip()
                if clean_line:
                    elements.append(Paragraph(clean_line, question_style))
                    elements.append(Spacer(1, 8))
            else:
                # Regular text line
                if line:
                    # Check if it's a question number or important text
                    if re.match(r'^[AB]?\d+\.', line) or 'Correct Answer:' in line:
                        elements.append(Paragraph(f"<b>{line}</b>", question_style))
                    else:
                        elements.append(Paragraph(line, question_style))
                    elements.append(Spacer(1, 6))
    
    # Build PDF
    try:
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Error building PDF: {str(e)}")
        return None

def create_enhanced_download_buttons(current_set_data, image_analyses, difficulty):
    """Create download buttons with PDF support"""
    col_d1, col_d2, col_d3 = st.columns(3)
    
    with col_d1:
        # Text download (existing)
        st.download_button(
            f"📄 Download Set {current_set_data['set_number']} (Text)",
            data=current_set_data['questions'],
            file_name=f"question_set_{current_set_data['set_number']}_{difficulty}_{int(time.time())}.txt",
            mime="text/plain"
        )
        
        # PDF download with images
        if image_analyses:
            try:
                with st.spinner("Generating PDF with images..."):
                    pdf_data = generate_pdf_with_images(
                        current_set_data, 
                        image_analyses, 
                        f"Question Set {current_set_data['set_number']} - {difficulty}"
                    )
                
                if pdf_data:
                    st.download_button(
                        f"📊 Download Set {current_set_data['set_number']} (PDF + Images)",
                        data=pdf_data,
                        file_name=f"question_set_{current_set_data['set_number']}_with_images_{difficulty}_{int(time.time())}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Failed to generate PDF")
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
    
    with col_d2:
        # All sets text download (existing functionality)
        all_sets_combined = ""
        for i, set_data in enumerate(st.session_state.generated_question_sets):
            all_sets_combined += f"""
{'='*60}
QUESTION SET {set_data['set_number']}
{'='*60}
Generated: {set_data['timestamp']}

{set_data['questions']}

"""
        
        # Include image information in the header
        image_info = ""
        if st.session_state.extracted_images:
            image_info = f"""
Images Analyzed: {len(st.session_state.extracted_images)}
Image Sources: {', '.join(set(img['source'] for img in st.session_state.extracted_images))}
"""
        
        formatted_all = f"""
COMPLETE QUESTION BANK - ALL SETS (WITH IMAGE DISPLAY)
======================================================
Difficulty: {difficulty if 'difficulty' in locals() else 'Medium'}
Questions per Set: {len(st.session_state.generated_question_sets[0]['questions'].split('A1.')) if st.session_state.generated_question_sets else 'N/A'}
Total Sets: {len(st.session_state.generated_question_sets)}
Total Questions: Approximately {len(st.session_state.generated_question_sets) * 25}
{image_info}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

{all_sets_combined}
"""
        
        st.download_button(
            "📦 Download All Sets (Text)",
            data=formatted_all,
            file_name=f"all_question_sets_with_images_{difficulty}_{int(time.time())}.txt",
            mime="text/plain"
        )
        
        # All sets PDF download
        if image_analyses:
            if st.button("📊 Generate All Sets PDF"):
                try:
                    with st.spinner("Generating comprehensive PDF with all sets..."):
                        # Generate combined PDF for all sets
                        combined_pdf_data = io.BytesIO()
                        doc = SimpleDocTemplate(combined_pdf_data, pagesize=A4)
                        elements = []
                        styles = getSampleStyleSheet()
                        
                        # Add title page
                        title_style = ParagraphStyle(
                            'MainTitle', parent=styles['Title'],
                            fontSize=20, spaceAfter=30, alignment=1
                        )
                        elements.append(Paragraph("Complete Question Bank - All Sets", title_style))
                        elements.append(Spacer(1, 50))
                        
                        # Process each set
                        for set_data in st.session_state.generated_question_sets:
                            set_title = f"Question Set {set_data['set_number']} - {difficulty}"
                            elements.append(Paragraph(set_title, styles['Heading1']))
                            elements.append(Spacer(1, 20))
                            
                            # Add set content (simplified - would need full implementation)
                            elements.append(Paragraph(set_data['questions'][:1000] + "...", styles['Normal']))
                            elements.append(Spacer(1, 30))
                        
                        doc.build(elements)
                        combined_pdf_data.seek(0)
                        
                        st.download_button(
                            "📊 Download Complete PDF",
                            data=combined_pdf_data.getvalue(),
                            file_name=f"all_question_sets_complete_{difficulty}_{int(time.time())}.pdf",
                            mime="application/pdf"
                        )
                        
                except Exception as e:
                    st.error(f"Error generating comprehensive PDF: {str(e)}")
    
    with col_d3:
        # Navigation buttons (existing)
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("⬅️ Previous", disabled=st.session_state.current_set == 0):
                st.session_state.current_set = max(0, st.session_state.current_set - 1)
                st.rerun()
        with col_nav2:
            if st.button("Next ➡️", disabled=st.session_state.current_set >= len(st.session_state.generated_question_sets) - 1):
                st.session_state.current_set = min(len(st.session_state.generated_question_sets) - 1, st.session_state.current_set + 1)
                st.rerun()

def display_question_set_with_images(set_data, image_analyses):
    """Display questions with embedded images"""
    questions_text = set_data['questions']
    
    # Split questions for processing
    question_blocks = questions_text.split('\n\nQ')
    if question_blocks:
        # Handle first question (doesn't have \n\n prefix)
        if question_blocks[0].startswith('Q'):
            first_q = question_blocks[0]
        else:
            first_q = 'Q' + question_blocks[0] if question_blocks[0] else ''
        
        # Handle remaining questions
        other_qs = ['Q' + block for block in question_blocks[1:] if block.strip()]
        
        all_questions = [first_q] + other_qs if first_q.strip() else other_qs
    else:
        all_questions = [questions_text]
    
    for i, question in enumerate(all_questions):
        if not question.strip():
            continue
            
        st.markdown(f"### Question {i+1}")
        
        # Check for image references in this question
        image_pattern = r'\[IMAGE:img_(\d+)\]'
        matches = re.findall(image_pattern, question)
        
        if matches:
            # Display images first, then question
            for match in matches:
                img_num = int(match) - 1
                if 0 <= img_num < len(image_analyses):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(
                            image_analyses[img_num]['image'], 
                            caption=f"Image {img_num + 1}: {image_analyses[img_num]['source']}",
                            width=300
                        )
                    with col2:
                        # Remove image reference from question text and display
                        clean_question = re.sub(image_pattern, '', question).strip()
                        st.markdown(clean_question)
        else:
            # Display question without image
            st.markdown(question)
        
        st.markdown("---")

def main():
    st.set_page_config(
        page_title="AI Question Generator with Image Analysis",
        page_icon="📝",
        layout="wide"
    )
    
    st.title("🎓 AI Question Generator with Image Display")
    st.markdown("Upload documents and generate **5 different question sets** with questions about text AND images shown in questions!")
    
    # Check API key
    api_key = get_openai_api_key()
    if not api_key:
        st.error("❌ OpenAI API key not found!")
        st.markdown("""
        **Setup Instructions:**
        1. Create a `.env` file in your project folder
        2. Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`
        3. Or add it to Streamlit secrets if deploying to cloud
        
        Get your API key from: https://platform.openai.com/account/api-keys
        """)
        st.stop()
    
    qg = QuestionGenerator()
    
    with st.sidebar:
        st.header("⚙️ Settings")
        st.success("✅ API Key Loaded")
        st.info("🖼️ Image Display Enabled")
        st.info("📊 PDF Download Available")
        
        # Debug information
        st.subheader("🐛 Debug Info")
        if st.button("Show API Key Status"):
            if api_key:
                st.success(f"✅ API Key loaded (starts with: {api_key[:10]}...)")
            else:
                st.error("❌ No API Key found")
        
        if st.button("🗑️ Clear All Data"):
            st.session_state.generated_question_sets = []
            st.session_state.current_set = 0
            st.session_state.extracted_images = []
            st.rerun()
        
        # Question Set Navigation
        if st.session_state.generated_question_sets:
            st.subheader("📚 Generated Sets")
            set_options = [f"Set {i+1}" for i in range(len(st.session_state.generated_question_sets))]
            selected_set = st.selectbox("Choose Set to View:", set_options, index=st.session_state.current_set)
            st.session_state.current_set = set_options.index(selected_set)
        
        # Show extracted images
        if st.session_state.extracted_images:
            st.subheader("🖼️ Extracted Images")
            st.write(f"Found {len(st.session_state.extracted_images)} images")
            if st.button("👁️ Show Image Preview"):
                for i, img_data in enumerate(st.session_state.extracted_images[:3]):  # Show first 3
                    st.image(img_data['image'], caption=f"Image {i+1}: {img_data['source']}", width=200)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📄 Upload Study Materials")
        uploaded_files = st.file_uploader(
            "Choose PDF, DOCX, or TXT files (max 2)",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Upload your study materials (PDFs and DOCX files will be scanned for images)"
        )
        
        if uploaded_files and len(uploaded_files) > 2:
            st.warning("Maximum 2 files allowed")
            uploaded_files = uploaded_files[:2]
        
        st.header("📄 (Optional) Reference Question Paper")
        ref_file = st.file_uploader(
            "Upload reference paper (PDF, DOCX, or TXT)",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=False,
            help="Upload a sample question paper to match the style (images will also be extracted)"
        )
        
        st.header("🔗 Web Links (Optional)")
        url1 = st.text_input("URL 1", placeholder="https://example.com/article")
        url2 = st.text_input("URL 2", placeholder="https://example.com/resource")
        
        st.header("⚙️ Question Settings")
        col_set1, col_set2 = st.columns(2)
        
        with col_set1:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
        
        with col_set2:
            num_questions = st.slider("Questions per Set", 5, 25, 12, 1)
        
        question_types = st.multiselect(
            "Select Question Types",
            ["Multiple Choice Questions (MCQ)", "Short Answer", "Long Answer", "Fill in the Blanks", "True/False"],
            default=["Multiple Choice Questions (MCQ)", "Short Answer"],
            help="Choose the types of questions you want to generate"
        )
        
        # Generate button
        generate_disabled = not uploaded_files and not url1.strip() and not url2.strip()
        
        # Info box about image feature
        st.info("🎯 **New Features**: Images will be displayed directly in questions! PDF downloads include embedded images!")
        
        if st.button("🚀 Generate 5 Question Sets with Images", type="primary", use_container_width=True, disabled=generate_disabled):
            if generate_disabled:
                st.error("❌ Please upload at least one file or provide a URL")
            else:
                # Show processing status
                with st.container():
                    st.subheader("📋 Processing Status")
                    
                    # Progress tracking
                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()
                    
                    all_content = ""
                    total_sources = len([f for f in uploaded_files if f] if uploaded_files else [])
                    total_sources += len([u for u in [url1, url2] if u.strip()])
                    
                    processed = 0
                    
                    # Process uploaded files
                    if uploaded_files:
                        for file in uploaded_files:
                            status_placeholder.info(f"Processing {file.name}...")
                            
                            if file.type == "application/pdf":
                                text = qg.extract_text_from_pdf(file)
                            elif "wordprocessingml" in file.type:
                                text = qg.extract_text_from_docx(file)
                            elif file.type == "text/plain":
                                text = qg.extract_text_from_txt(file)
                            else:
                                st.warning(f"⚠️ Unsupported file type: {file.type}")
                                text = ""
                            
                            if text.strip():
                                all_content += f"\n\n=== Content from {file.name} ===\n{text}"
                            
                            processed += 1
                            progress_placeholder.progress(processed / total_sources)
                    
                    # Process URLs
                    for i, url in enumerate([url1, url2], 1):
                        if url.strip():
                            status_placeholder.info(f"Processing URL {i}...")
                            text = qg.extract_text_from_url(url.strip())
                            
                            if text.strip():
                                all_content += f"\n\n=== Content from URL {i} ===\n{text}"
                            
                            processed += 1
                            progress_placeholder.progress(processed / total_sources)
                    
                    # Process reference file
                    reference_style = ""
                    if ref_file:
                        status_placeholder.info("Processing reference paper...")
                        
                        if ref_file.type == "application/pdf":
                            reference_style = qg.extract_text_from_pdf(ref_file)
                        elif "wordprocessingml" in ref_file.type:
                            reference_style = qg.extract_text_from_docx(ref_file)
                        elif ref_file.type == "text/plain":
                            reference_style = qg.extract_text_from_txt(ref_file)
                        
                        if reference_style.strip():
                            st.info("📄 Reference paper style will be used for question formatting.")
                    
                    # Clear initial progress indicators
                    progress_placeholder.empty()
                    status_placeholder.empty()
                    
                    # Process images from all sources - FIXED BUG HERE
                    st.subheader("🖼️ Image Processing")
                    urls_list = [url for url in [url1, url2] if url.strip()]
                    
                    # FIX: Handle ref_file properly - ensure it's passed as expected
                    ref_files_list = []
                    if ref_file is not None:
                        # ref_file should be a single file object from st.file_uploader
                        if hasattr(ref_file, 'type'):  # Valid file object
                            ref_files_list = [ref_file]  # Wrap in list for consistency
                        else:
                            st.warning(f"⚠️ Reference file has unexpected format: {type(ref_file)}")
                    
                    # Pass the processed ref_files_list instead of ref_file directly
                    image_analyses = qg.image_processor.process_all_images(uploaded_files, urls_list, ref_files_list)
                    
                    # Store in session state for display
                    st.session_state.extracted_images = image_analyses
                    
                    # Check if we have content
                    if all_content.strip() or image_analyses:
                        if all_content.strip():
                            st.success(f"✅ Successfully extracted {len(all_content)} characters from all sources")
                        if image_analyses:
                            st.success(f"✅ Successfully analyzed {len(image_analyses)} images")
                        
                        # Generate multiple question sets
                        st.subheader("🎯 Generating 5 Unique Question Sets")
                        question_sets = qg.generate_multiple_question_sets(
                            all_content, difficulty, num_questions, question_types, reference_style, image_analyses, 5
                        )
                        
                        if question_sets:
                            st.session_state.generated_question_sets = question_sets
                            st.session_state.current_set = 0
                            st.success(f"🎉 Generated {len(question_sets)} question sets successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Failed to generate question sets. Please try again.")
                    else:
                        st.error("❌ No content or images could be extracted from any source. Please check your files and URLs.")
                        
                        # Show debugging info
                        st.subheader("🐛 Debug Information")
                        st.write(f"Files uploaded: {len(uploaded_files) if uploaded_files else 0}")
                        st.write(f"URLs provided: {len([u for u in [url1, url2] if u.strip()])}")
                        st.write(f"Images found: {len(image_analyses)}")
                        
                        if uploaded_files:
                            for file in uploaded_files:
                                st.write(f"- {file.name}: {file.size} bytes, type: {file.type}")
    
    with col2:
        st.header("📊 Summary")
        
        if uploaded_files:
            st.subheader("📁 Files")
            for file in uploaded_files:
                file_size = file.size / 1024  # Convert to KB
                st.write(f"• {file.name} ({file_size:.1f} KB)")
        
        if ref_file:
            st.subheader("📄 Reference Paper")
            st.write(f"• {ref_file.name}")
        
        urls = [url for url in [url1, url2] if url.strip()]
        if urls:
            st.subheader("🌐 URLs")
            for i, url in enumerate(urls, 1):
                st.write(f"• URL {i}: {url[:30]}{'...' if len(url) > 30 else ''}")
        
        st.subheader("⚙️ Settings")
        if 'difficulty' in locals():
            st.write(f"**Difficulty:** {difficulty}")
            st.write(f"**Questions per Set:** {num_questions}")
            st.write(f"**Total Sets:** 5")
            st.write(f"**Total Questions:** {num_questions * 5}")
            if 'question_types' in locals() and question_types:
                st.write(f"**Types:** {', '.join(question_types[:2])}{'...' if len(question_types) > 2 else ''}")
        
        # Set variation info
        if st.session_state.generated_question_sets:
            st.subheader("🎯 Set Variations")
            variations = [
                "Theoretical concepts",
                "Practical applications", 
                "Analytical problems",
                "Comparative analysis",
                "Higher-order thinking"
            ]
            for i, var in enumerate(variations):
                st.write(f"**Set {i+1}:** {var}")
        
        # Image analysis summary
        if st.session_state.extracted_images:
            st.subheader("🖼️ Image Analysis")
            st.write(f"**Images Found:** {len(st.session_state.extracted_images)}")
            st.write("**Sources:**")
            sources = set(img['source'] for img in st.session_state.extracted_images)
            for source in list(sources)[:3]:
                st.write(f"• {source}")
            if len(sources) > 3:
                st.write(f"• ... and {len(sources) - 3} more")
    
    # Display results for selected set
    if st.session_state.generated_question_sets:
        current_set_data = st.session_state.generated_question_sets[st.session_state.current_set]
        
        st.header(f"📝 Question Set {current_set_data['set_number']}")
        
        # NEW: Use enhanced download buttons with PDF support
        create_enhanced_download_buttons(current_set_data, st.session_state.extracted_images, difficulty)
        
        # Show character count and image info
        char_count = len(current_set_data['questions'])
        image_count = len(st.session_state.extracted_images)
        st.caption(f"Set {current_set_data['set_number']} - {char_count} characters - {image_count} images analyzed - Generated: {current_set_data['timestamp']}")
        
        # Display current set questions with images
        st.subheader(f"Questions - Set {current_set_data['set_number']}:")
        
        # Toggle between formatted view and raw text
        view_mode = st.radio(
            "Display Mode:",
            ["📖 Formatted View (with Images)", "📝 Raw Text"],
            horizontal=True
        )
        
        if view_mode == "📖 Formatted View (with Images)":
            if st.session_state.extracted_images:
                st.info("🖼️ Images will be displayed directly above related questions")
            display_question_set_with_images(current_set_data, st.session_state.extracted_images)
        else:
            st.text_area(
                f"Raw Questions - Set {current_set_data['set_number']}:",
                value=current_set_data['questions'],
                height=400
            )
        
        # Show overview of all sets
        if len(st.session_state.generated_question_sets) > 1:
            with st.expander(f"📚 Overview of All {len(st.session_state.generated_question_sets)} Sets"):
                for i, set_data in enumerate(st.session_state.generated_question_sets):
                    st.write(f"**Set {set_data['set_number']}** - {len(set_data['questions'])} characters - Generated: {set_data['timestamp']}")
        
        # Show image analysis details
        if st.session_state.extracted_images:
            with st.expander(f"🖼️ Image Analysis Details ({len(st.session_state.extracted_images)} images)"):
                for i, img_data in enumerate(st.session_state.extracted_images):
                    st.write(f"**Image {i+1}:** {img_data['source']}")
                    with st.expander(f"View Image {i+1} & Analysis"):
                        col_img1, col_img2 = st.columns([1, 2])
                        with col_img1:
                            st.image(img_data['image'], caption=f"Image {i+1}", width=200)
                        with col_img2:
                            st.write("**AI Analysis:**")
                            st.write(img_data['analysis'][:500] + "..." if len(img_data['analysis']) > 500 else img_data['analysis'])

if __name__ == "__main__":
    main()