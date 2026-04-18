import streamlit as st
import requests
import base64
import urllib.parse

st.set_page_config(page_title="CloudShare REST API", layout="wide", initial_sidebar_state="expanded")

# Custom styling for CloudShare REST API
st.markdown("""
    <style>
    /* Main background and text colors */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 2px solid #3b82f6;
    }
    
    /* Title styling */
    h1 {
        color: #60a5fa !important;
        text-shadow: 0 0 10px rgba(96, 165, 250, 0.5);
    }
    
    h2, h3 {
        color: #93c5fd !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: 1px solid #1e40af !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%) !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.5) !important;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 6px !important;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 6px !important;
    }
    
    /* Markdown text color */
    p, span {
        color: #cbd5e1 !important;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.1) !important;
        border: 1px solid #22c55e !important;
        border-radius: 6px !important;
    }
    
    .stError {
        background-color: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid #ef4444 !important;
        border-radius: 6px !important;
    }
    
    .stInfo {
        background-color: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 6px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state variables to store authentication token and user data
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None


def get_headers():
    """Get authorization headers with JWT token for API requests."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def login_page():
    """Display the login and signup page."""
    st.title("☁️ CloudShare REST API")
    st.write("*Secure cloud storage and sharing platform*")

    # Create login form
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")

    if email and password:
        col1, col2 = st.columns(2)

        # Login button
        with col1:
            if st.button("Login", type="primary", use_container_width=True):
                # Send login request to FastAPI backend
                login_data = {"username": email, "password": password}
                response = requests.post("http://localhost:8000/auth/jwt/login", data=login_data)

                if response.status_code == 200:
                    # Save token and user data to session state
                    token_data = response.json()
                    st.session_state.token = token_data["access_token"]

                    # Fetch current user info with the new token
                    user_response = requests.get("http://localhost:8000/users/me", headers=get_headers())
                    if user_response.status_code == 200:
                        st.session_state.user = user_response.json()
                        st.rerun()  # Rerun to show feed page
                    else:
                        st.error("Failed to get user info")
                else:
                    st.error("Invalid email or password!")

        # Sign up button
        with col2:
            if st.button("Sign Up", type="secondary", use_container_width=True):
                # Send registration request to backend
                signup_data = {"email": email, "password": password}
                response = requests.post("http://localhost:8000/auth/register", json=signup_data)

                if response.status_code == 201:
                    st.success("Account created! Click Login now.")
                else:
                    error_detail = response.json().get("detail", "Registration failed")
                    st.error(f"Registration failed: {error_detail}")
    else:
        st.info("Enter your email and password above")


def upload_page():
    """Display the media upload page."""
    st.title("� Upload & Share")

    # File uploader for images and videos
    uploaded_file = st.file_uploader("Choose media", type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm'])
    # Text area for post caption
    caption = st.text_area("Caption:", placeholder="What's on your mind?")

    if uploaded_file and st.button("Share", type="primary"):
        with st.spinner("Uploading..."):
            # Prepare file and data for API request
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"caption": caption}
            # Send upload request to backend
            response = requests.post("http://localhost:8000/upload", files=files, data=data, headers=get_headers())

            if response.status_code == 200:
                st.success("Posted!")
                st.rerun()  # Refresh to show new post in feed
            else:
                st.error("Upload failed!")


def encode_text_for_overlay(text):
    """Encode text for ImageKit overlay - applies base64 then URL encoding.
    
    This is required by ImageKit's text overlay transformation API.
    """
    if not text:
        return ""
    # Base64 encode the text
    base64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    # URL encode the result to handle special characters
    return urllib.parse.quote(base64_text)


def create_transformed_url(original_url, transformation_params, caption=None):
    """Create an ImageKit URL with transformations applied (resizing, overlays, etc.).
    
    Args:
        original_url: The original ImageKit URL
        transformation_params: ImageKit transformation string (e.g., "w-400,h-300")
        caption: Optional caption text to overlay on the image
    
    Returns:
        Modified URL with transformations applied
    """
    if caption:
        # Build text overlay transformation with base64 encoded caption
        encoded_caption = encode_text_for_overlay(caption)
        # Add text overlay at bottom with semi-transparent background
        text_overlay = f"l-text,ie-{encoded_caption},ly-N20,lx-20,fs-100,co-white,bg-000000A0,l-end"
        transformation_params = text_overlay

    if not transformation_params:
        return original_url

    # Parse ImageKit URL structure and inject transformations
    parts = original_url.split("/")
    imagekit_id = parts[3]
    file_path = "/".join(parts[4:])
    base_url = "/".join(parts[:4])
    # Insert /tr:{transformation} path segment for ImageKit API
    return f"{base_url}/tr:{transformation_params}/{file_path}"


def feed_page():
    """Display the social feed with all posts."""
    st.title("☁️ Cloud Feed")

    # Fetch all posts from backend
    response = requests.get("http://localhost:8000/feed", headers=get_headers())
    if response.status_code == 200:
        posts = response.json()["posts"]

        if not posts:
            st.info("No posts yet! Be the first to share something.")
            return

        # Display each post
        for post in posts:
            st.markdown("---")

            # Display post header with author, date, and delete button (if current user is owner)
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{post['email']}** • {post['created_at'][:10]}")
            with col2:
                if post.get('is_owner', False):
                    if st.button("🗑️", key=f"delete_{post['id']}", help="Delete post"):
                        # Send delete request to backend
                        response = requests.delete(f"http://localhost:8000/posts/{post['id']}", headers=get_headers())
                        if response.status_code == 200:
                            st.success("Post deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete post!")

            # Display media (image or video) with caption overlay
            caption = post.get('caption', '')
            if post['file_type'] == 'image':
                # Apply transformations to image including caption overlay
                uniform_url = create_transformed_url(post['url'], "", caption)
                st.image(uniform_url, width=300)
            else:
                # For videos: resize and pad to maintain aspect ratio with caption overlay
                uniform_video_url = create_transformed_url(post['url'], "w-400,h-200,cm-pad_resize,bg-blurred")
                st.video(uniform_video_url, width=300)
                st.caption(caption)  # Display caption below video

            st.markdown("")  # Space between posts
    else:
        st.error("Failed to load feed")


# Main app logic - show login or main navigation based on authentication state
if st.session_state.user is None:
    # User not logged in - show login/signup page
    login_page()
else:
    # User logged in - show sidebar navigation
    st.sidebar.title(f"☁️ CloudShare")
    st.sidebar.write(f"*Connected as: {st.session_state.user['email']}*")
    st.sidebar.markdown("---")

    # Logout button
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    st.sidebar.markdown("---")
    # Navigation between feed and upload pages
    page = st.sidebar.radio("📋 Navigate:", ["☁️ Cloud Feed", "📤 Upload & Share"])

    if page == "☁️ Cloud Feed":
        feed_page()
    else:
        upload_page()
