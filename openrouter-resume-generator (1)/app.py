from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_from_directory
import sqlite3
import requests
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
import base64
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROFILE_PHOTOS'] = 'static/profile_photos'
app.config['TEMPLATE_THUMBNAILS'] = 'static/template_thumbnails'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROFILE_PHOTOS'], exist_ok=True)
os.makedirs(app.config['TEMPLATE_THUMBNAILS'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    
    # Templates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            folder TEXT NOT NULL,
            thumbnail TEXT,
            html_content TEXT,
            css_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Admin users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # User resumes table for saving drafts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            resume_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default admin user
    cursor.execute('SELECT COUNT(*) FROM admin_users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        password_hash = generate_password_hash('admin123')
        cursor.execute('INSERT INTO admin_users (username, password_hash) VALUES (?, ?)', 
                      ('admin', password_hash))
    
    # Insert default templates
    cursor.execute('SELECT COUNT(*) FROM templates')
    if cursor.fetchone()[0] == 0:
        # Template 1: Professional Modern
        default_html_1 = '''
<div class="resume-container modern-template">
    <div class="resume-header">
        {% if show_profile_photo and profile_photo %}
        <div class="profile-section">
            <img src="{{ profile_photo }}" alt="Profile Photo" class="profile-image">
        </div>
        {% endif %}
        <div class="header-info">
            <h1 class="name">{{ name }}</h1>
            <div class="contact-details">
                {% if email %}<div class="contact-item"><i class="fas fa-envelope"></i>{{ email }}</div>{% endif %}
                {% if location %}<div class="contact-item"><i class="fas fa-map-marker-alt"></i>{{ location }}</div>{% endif %}
                {% if address %}<div class="contact-item"><i class="fas fa-home"></i>{{ address }}</div>{% endif %}
            </div>
        </div>
    </div>

    <div class="resume-body">
        <div class="left-column">
            {% if show_about and about_me %}
            <section class="section">
                <h2 class="section-title">Professional Summary</h2>
                <div class="editable-content" data-field="about_me">{{ about_me }}</div>
            </section>
            {% endif %}

            {% if show_skills and skill_list %}
            <section class="section">
                <h2 class="section-title">Skills</h2>
                {% for skill in skill_list %}
                <div class="skill-group">
                    <h3 class="skill-category">{{ skill.category }}</h3>
                    <div class="skill-items">{{ skill.skills }}</div>
                </div>
                {% endfor %}
            </section>
            {% endif %}

            {% if show_interests and interest_list %}
            <section class="section">
                <h2 class="section-title">Interests</h2>
                <div class="interests-container">
                    {% for interest in interest_list %}
                    <span class="interest-item">{{ interest }}</span>
                    {% endfor %}
                </div>
            </section>
            {% endif %}
        </div>

        <div class="right-column">
            {% if show_experience and experience_list %}
            <section class="section">
                <h2 class="section-title">Experience</h2>
                {% if experience_summary %}
                <div class="editable-content summary" data-field="experience_summary">{{ experience_summary }}</div>
                {% endif %}
                {% for exp in experience_list %}
                <div class="experience-item">
                    <h3 class="job-title">{{ exp.job_role }}</h3>
                    <div class="company-info">{{ exp.organization }} | {{ exp.duration }}</div>
                    {% if exp.description %}<p class="job-description">{{ exp.description }}</p>{% endif %}
                </div>
                {% endfor %}
            </section>
            {% endif %}

            {% if show_education and education_list %}
            <section class="section">
                <h2 class="section-title">Education</h2>
                {% for edu in education_list %}
                <div class="education-item">
                    <h3 class="degree">{{ edu.course_name }}</h3>
                    <div class="school-info">{{ edu.university_name }} | {{ edu.duration }}</div>
                    {% if edu.grade %}<div class="grade">{{ edu.grade }}</div>{% endif %}
                </div>
                {% endfor %}
            </section>
            {% endif %}

            {% if show_projects and project_list %}
            <section class="section">
                <h2 class="section-title">Projects</h2>
                {% if project_summary %}
                <div class="editable-content summary" data-field="project_summary">{{ project_summary }}</div>
                {% endif %}
                {% for project in project_list %}
                <div class="project-item">
                    <h3 class="project-name">{{ project.name }}</h3>
                    <div class="project-tech">
                        {% if project.languages %}
                            {% for lang in project.languages %}{{ lang }}{% if not loop.last %}, {% endif %}{% endfor %}
                        {% endif %}
                    </div>
                    {% if project.description %}<p class="project-description">{{ project.description }}</p>{% endif %}
                </div>
                {% endfor %}
            </section>
            {% endif %}
        </div>
    </div>
</div>
'''
        
        default_css_1 = '''
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

.modern-template {
    font-family: 'Poppins', sans-serif;
    max-width: 850px;
    margin: 0 auto;
    background: white;
    box-shadow: 0 0 30px rgba(0,0,0,0.1);
    line-height: 1.6;
    color: #333;
}

.resume-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px;
    display: flex;
    align-items: center;
    gap: 30px;
}

.profile-image {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 4px solid white;
    object-fit: cover;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.name {
    font-size: 2.5em;
    font-weight: 700;
    margin: 0 0 15px 0;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.contact-details {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
}

.contact-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
}

.contact-item i {
    width: 16px;
    opacity: 0.9;
}

.resume-body {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 0;
}

.left-column {
    background: #f8f9fa;
    padding: 40px 30px;
}

.right-column {
    padding: 40px 30px;
}

.section {
    margin-bottom: 35px;
}

.section-title {
    color: #667eea;
    font-size: 1.4em;
    font-weight: 600;
    margin-bottom: 20px;
    text-transform: uppercase;
    letter-spacing: 1px;
    position: relative;
    padding-bottom: 10px;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 50px;
    height: 3px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 2px;
}

.editable-content {
    background: rgba(102, 126, 234, 0.1);
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    margin-bottom: 15px;
    transition: all 0.3s ease;
}

.editable-content:hover {
    background: rgba(102, 126, 234, 0.15);
    transform: translateX(2px);
}

.skill-group {
    margin-bottom: 20px;
}

.skill-category {
    color: #333;
    font-size: 1.1em;
    font-weight: 600;
    margin-bottom: 8px;
}

.skill-items {
    color: #666;
    line-height: 1.8;
}

.interests-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.interest-item {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.9em;
    font-weight: 500;
}

.experience-item, .education-item, .project-item {
    margin-bottom: 25px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

.experience-item:last-child, .education-item:last-child, .project-item:last-child {
    border-bottom: none;
}

.job-title, .degree, .project-name {
    color: #333;
    font-size: 1.2em;
    font-weight: 600;
    margin-bottom: 5px;
}

.company-info, .school-info, .project-tech {
    color: #667eea;
    font-weight: 500;
    margin-bottom: 8px;
}

.job-description, .project-description {
    color: #666;
    margin-top: 10px;
}

.grade {
    color: #28a745;
    font-weight: 500;
    font-size: 0.9em;
}

.summary {
    margin-bottom: 25px;
}

@media (max-width: 768px) {
    .resume-body {
        grid-template-columns: 1fr;
    }
    
    .resume-header {
        flex-direction: column;
        text-align: center;
    }
    
    .name {
        font-size: 2em;
    }
    
    .contact-details {
        justify-content: center;
    }
}

@media print {
    .modern-template {
        box-shadow: none;
    }
    
    .editable-content {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
}
'''
        
        cursor.execute('''
            INSERT INTO templates (name, folder, html_content, css_content) 
            VALUES (?, ?, ?, ?)
        ''', ('Professional Modern', 'modern', default_html_1, default_css_1))
    
    conn.commit()
    conn.close()

def get_openrouter_api_key():
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('openrouter_api_key',))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def generate_ai_content(user_data):
    api_key = get_openrouter_api_key()
    if not api_key:
        return {"error": "OpenRouter API key not configured"}
    
    # Build comprehensive prompt with all user data
    prompt = f"""You are a professional resume writing assistant. Generate high-quality, ATS-friendly resume content based on the user's information.

🎯 Generate the following sections:

1. **About Me (Professional Summary)**
   A well-structured 4-5 line summary highlighting education, skills, experience, and overall profile.

2. **Project Summary**
   A 2-3 line summary of projects focusing on technologies and outcomes. Only if projects exist.

3. **Experience Summary**
   A 2-3 line summary of work experience highlighting roles and contributions. Only if experience exists.

🧾 User Information:
Name: {user_data.get('name', '')}
Location: {user_data.get('location', '')}
Email: {user_data.get('email', '')}

Education:"""
    
    # Add education details
    if user_data.get('education_list'):
        for edu in user_data['education_list']:
            prompt += f"\n- {edu.get('course_name', '')} from {edu.get('university_name', '')} ({edu.get('duration', '')}) - Grade: {edu.get('grade', 'N/A')}"
    
    prompt += "\n\nSkills:"
    if user_data.get('skill_list'):
        for skill in user_data['skill_list']:
            prompt += f"\n- {skill.get('category', '')}: {skill.get('skills', '')}"
    
    prompt += "\n\nProjects:"
    if user_data.get('project_list'):
        for project in user_data['project_list']:
            languages = ', '.join(project.get('languages', []))
            prompt += f"\n- {project.get('name', '')} using {languages}: {project.get('description', '')}"
    
    prompt += "\n\nExperience:"
    if user_data.get('experience_list'):
        for exp in user_data['experience_list']:
            prompt += f"\n- {exp.get('job_role', '')} at {exp.get('organization', '')} ({exp.get('duration', '')}): {exp.get('description', '')}"
    
    prompt += f"\n\nInterests: {', '.join(user_data.get('interest_list', []))}"
    
    prompt += """

📌 Instructions:
- Generate content only for sections with data
- Be concise and professional
- Avoid repetition across sections
- Use clear, ATS-friendly language
- Output only content blocks without headings

📤 Output Format:
About Me:
[Your content here]

Project Summary:
[Your content here]

Experience Summary:
[Your content here]"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1000
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse the AI response
            sections = {}
            current_section = None
            current_content = []
            
            for line in content.split('\n'):
                line = line.strip()
                if line.endswith(':') and line.replace(':', '') in ['About Me', 'Project Summary', 'Experience Summary']:
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = line.replace(':', '')
                    current_content = []
                elif line and current_section:
                    current_content.append(line)
            
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            
            return sections
        else:
            return {"error": f"API request failed: {response.status_code}"}
    
    except Exception as e:
        return {"error": f"Error generating content: {str(e)}"}

def render_template_string(template_string, **context):
    """
    Render a Jinja2 template string with the given context.
    This function avoids recursion issues by using a simple approach.
    """
    try:
        from jinja2 import Template
        
        # Create template directly from string
        template = Template(template_string)
        
        # Render with context
        return template.render(**context)
    except Exception as e:
        raise Exception(f"Template rendering failed: {str(e)}")

@app.route('/')
def index():
    return redirect(url_for('template_gallery'))

@app.route('/templates')
def template_gallery():
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, thumbnail FROM templates ORDER BY created_at DESC')
    templates = cursor.fetchall()
    conn.close()
    
    return render_template('template_gallery.html', templates=templates)

@app.route('/create/<int:template_id>')
def create_resume(template_id):
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM templates WHERE id = ?', (template_id,))
    template = cursor.fetchone()
    conn.close()
    
    if not template:
        flash('Template not found')
        return redirect(url_for('template_gallery'))
    
    return render_template('create_resume.html', template={'id': template[0], 'name': template[1]})

@app.route('/upload_profile_photo', methods=['POST'])
def upload_profile_photo():
    if 'profile_photo' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['profile_photo']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(app.config['PROFILE_PHOTOS'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': f'/profile_photos/{filename}'
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/profile_photos/<filename>')
def profile_photo(filename):
    return send_from_directory(app.config['PROFILE_PHOTOS'], filename)

@app.route('/template_thumbnails/<filename>')
def template_thumbnail(filename):
    return send_from_directory(app.config['TEMPLATE_THUMBNAILS'], filename)

@app.route('/admin')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    username = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM admin_users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and check_password_hash(result[0], password):
        session['admin_logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM templates ORDER BY created_at DESC')
    templates = cursor.fetchall()
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('openrouter_api_key',))
    api_key = cursor.fetchone()
    conn.close()
    
    return render_template('admin_dashboard.html', templates=templates, api_key=api_key[0] if api_key else '')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/update_api_key', methods=['POST'])
def update_api_key():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    api_key = request.form['api_key']
    
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', 
                  ('openrouter_api_key', api_key))
    conn.commit()
    conn.close()
    
    flash('API key updated successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_template', methods=['POST'])
def add_template():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    name = request.form['name']
    html_content = request.form['html_content']
    css_content = request.form['css_content']
    
    # Handle thumbnail upload
    thumbnail_filename = None
    if 'thumbnail' in request.files and request.files['thumbnail'].filename != '':
        file = request.files['thumbnail']
        if file and allowed_file(file.filename):
            thumbnail_filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
            filepath = os.path.join(app.config['TEMPLATE_THUMBNAILS'], thumbnail_filename)
            file.save(filepath)
    
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO templates (name, folder, thumbnail, html_content, css_content) 
        VALUES (?, ?, ?, ?, ?)
    ''', (name, name.lower().replace(' ', '_'), thumbnail_filename, html_content, css_content))
    conn.commit()
    conn.close()
    
    flash('Template added successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_template/<int:template_id>')
def edit_template(template_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
    template = cursor.fetchone()
    conn.close()
    
    if not template:
        flash('Template not found')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_template.html', template=template)

@app.route('/admin/update_template/<int:template_id>', methods=['POST'])
def update_template(template_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    name = request.form['name']
    html_content = request.form['html_content']
    css_content = request.form['css_content']
    
    # Handle thumbnail upload
    thumbnail_filename = request.form.get('existing_thumbnail')
    if 'thumbnail' in request.files and request.files['thumbnail'].filename != '':
        file = request.files['thumbnail']
        if file and allowed_file(file.filename):
            thumbnail_filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
            filepath = os.path.join(app.config['TEMPLATE_THUMBNAILS'], thumbnail_filename)
            file.save(filepath)
    
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE templates 
        SET name = ?, folder = ?, thumbnail = ?, html_content = ?, css_content = ?
        WHERE id = ?
    ''', (name, name.lower().replace(' ', '_'), thumbnail_filename, html_content, css_content, template_id))
    conn.commit()
    conn.close()
    
    flash('Template updated successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_template/<int:template_id>', methods=['POST'])
def delete_template(template_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
    conn.commit()
    conn.close()
    
    flash('Template deleted successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    user_data = request.json
    
    # Generate AI content
    ai_content = generate_ai_content(user_data)
    
    if 'error' in ai_content:
        return jsonify(ai_content), 400
    
    # Get template
    template_id = user_data.get('template_id', 1)
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT html_content, css_content FROM templates WHERE id = ?', (template_id,))
    template = cursor.fetchone()
    conn.close()
    
    if not template:
        return jsonify({"error": "Template not found"}), 404
    
    html_content, css_content = template
    
    # Prepare template data
    template_data = {**user_data}
    template_data.update({
        'about_me': ai_content.get('About Me', ''),
        'project_summary': ai_content.get('Project Summary', ''),
        'experience_summary': ai_content.get('Experience Summary', '')
    })
    
    # Ensure all required lists exist
    for list_key in ['education_list', 'skill_list', 'experience_list', 'project_list', 'interest_list']:
        if list_key not in template_data:
            template_data[list_key] = []
    
    # Render template
    try:
        processed_html = render_template_string(html_content, **template_data)
        
        return jsonify({
            'html': processed_html,
            'css': css_content,
            'ai_content': ai_content,
            'template_data': template_data
        })
    except Exception as e:
        return jsonify({"error": f"Template rendering error: {str(e)}"}), 500

@app.route('/update_ai_content', methods=['POST'])
def update_ai_content():
    data = request.json
    field = data.get('field')
    content = data.get('content')
    user_data = data.get('user_data', {})
    
    # Generate new AI content for specific field
    ai_content = generate_ai_content(user_data)
    
    if 'error' in ai_content:
        return jsonify(ai_content), 400
    
    return jsonify({
        'success': True,
        'new_content': ai_content.get(field.replace('_', ' ').title(), content)
    })

@app.route('/get_templates')
def get_templates():
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM templates')
    templates = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(templates)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    user_data = request.json
    
    # Generate AI content
    ai_content = generate_ai_content(user_data)
    
    if 'error' in ai_content:
        return jsonify(ai_content), 400
    
    # Get template
    template_id = user_data.get('template_id', 1)
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT html_content, css_content FROM templates WHERE id = ?', (template_id,))
    template = cursor.fetchone()
    conn.close()
    
    if not template:
        return jsonify({"error": "Template not found"}), 404
    
    html_content, css_content = template
    
    # Merge AI content with user data
    template_data = {**user_data}
    template_data.update({
        'about_me': ai_content.get('About Me', ''),
        'project_summary': ai_content.get('Project Summary', ''),
        'experience_summary': ai_content.get('Experience Summary', '')
    })
    
    # Ensure all required lists exist
    for list_key in ['education_list', 'skill_list', 'experience_list', 'project_list', 'interest_list']:
        if list_key not in template_data:
            template_data[list_key] = []
    
    # Render template
    try:
        processed_html = render_template_string(html_content, **template_data)
        
        # Clean HTML for PDF (remove editable classes and attributes)
        import re
        clean_html = re.sub(r'class="editable-content"[^>]*data-field="[^"]*"', 'class="content-section"', processed_html)
        clean_html = re.sub(r'contenteditable="[^"]*"', '', clean_html)
        
        # Add PDF-specific CSS
        pdf_css = css_content + '''
        .content-section {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            cursor: default !important;
        }
        .edit-controls {
            display: none !important;
        }
        '''
        
        return jsonify({
            'html': clean_html,
            'css': pdf_css
        })
    except Exception as e:
        return jsonify({"error": f"Template rendering error: {str(e)}"}), 500

@app.route('/admin/test_template/<int:template_id>')
def test_template(template_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
    template = cursor.fetchone()
    conn.close()
    
    if not template:
        flash('Template not found')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('test_template.html', template=template)

@app.route('/admin/preview_template', methods=['POST'])
def preview_template():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    template_id = data.get('template_id')
    test_data = data.get('test_data', {})
    
    # Get template
    conn = sqlite3.connect('resume_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT html_content, css_content FROM templates WHERE id = ?', (template_id,))
    template = cursor.fetchone()
    conn.close()
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    html_content, css_content = template
    
    # Use test data or generate sample data
    if not test_data:
        test_data = generate_sample_data()
    
    # Ensure all required lists exist
    for list_key in ['education_list', 'skill_list', 'experience_list', 'project_list', 'interest_list']:
        if list_key not in test_data:
            test_data[list_key] = []
    
    # Render template
    try:
        processed_html = render_template_string(html_content, **test_data)
        
        return jsonify({
            'html': processed_html,
            'css': css_content,
            'test_data': test_data
        })
    except Exception as e:
        return jsonify({'error': f'Template rendering error: {str(e)}'}), 500

def generate_sample_data():
    return {
        'name': 'John Alexander Smith',
        'email': 'john.smith@email.com',
        'location': 'San Francisco, CA',
        'address': '123 Tech Street, San Francisco, CA 94105',
        'profile_photo': '/static/sample-profile.jpg',
        'show_profile_photo': True,
        'show_about': True,
        'show_education': True,
        'show_experience': True,
        'show_projects': True,
        'show_skills': True,
        'show_interests': True,
        'about_me': 'Experienced software engineer with 5+ years of expertise in full-stack development, cloud architecture, and team leadership. Proven track record of delivering scalable solutions and driving technical innovation in fast-paced environments.',
        'project_summary': 'Led development of multiple high-impact projects including e-commerce platforms, mobile applications, and enterprise software solutions with focus on performance and user experience.',
        'experience_summary': 'Progressive career growth from junior developer to senior engineer, with experience in startups and enterprise environments, specializing in modern web technologies and agile methodologies.',
        'education_list': [
            {
                'course_name': 'Master of Science in Computer Science',
                'university_name': 'Stanford University',
                'duration': '2018-2020',
                'grade': '3.9 GPA'
            },
            {
                'course_name': 'Bachelor of Science in Software Engineering',
                'university_name': 'UC Berkeley',
                'duration': '2014-2018',
                'grade': '3.7 GPA, Magna Cum Laude'
            }
        ],
        'skill_list': [
            {
                'category': 'Programming Languages',
                'skills': 'JavaScript, Python, Java, TypeScript, Go, Rust'
            },
            {
                'category': 'Frontend Technologies',
                'skills': 'React, Vue.js, Angular, HTML5, CSS3, Sass, Tailwind CSS'
            },
            {
                'category': 'Backend Technologies',
                'skills': 'Node.js, Django, Flask, Spring Boot, Express.js'
            },
            {
                'category': 'Cloud & DevOps',
                'skills': 'AWS, Docker, Kubernetes, CI/CD, Terraform, Jenkins'
            },
            {
                'category': 'Databases',
                'skills': 'PostgreSQL, MongoDB, Redis, MySQL, DynamoDB'
            }
        ],
        'experience_list': [
            {
                'job_role': 'Senior Software Engineer',
                'organization': 'TechCorp Solutions',
                'duration': 'Jan 2022 - Present',
                'description': 'Lead a team of 5 developers in building scalable web applications. Architected microservices infrastructure serving 1M+ users. Implemented CI/CD pipelines reducing deployment time by 60%. Mentored junior developers and conducted technical interviews.'
            },
            {
                'job_role': 'Full Stack Developer',
                'organization': 'StartupXYZ',
                'duration': 'Jun 2020 - Dec 2021',
                'description': 'Developed and maintained React-based frontend and Node.js backend systems. Built RESTful APIs and integrated third-party services. Optimized database queries improving application performance by 40%. Collaborated with product team on feature development.'
            },
            {
                'job_role': 'Software Developer Intern',
                'organization': 'Google',
                'duration': 'Summer 2019',
                'description': 'Worked on Google Cloud Platform tools, developing internal dashboard applications. Implemented automated testing frameworks and contributed to open-source projects. Gained experience with large-scale distributed systems.'
            }
        ],
        'project_list': [
            {
                'name': 'E-Commerce Platform',
                'languages': ['React', 'Node.js', 'PostgreSQL', 'AWS'],
                'description': 'Built a full-stack e-commerce platform with payment integration, inventory management, and admin dashboard. Handles 10,000+ daily transactions with 99.9% uptime.'
            },
            {
                'name': 'Mobile Task Manager',
                'languages': ['React Native', 'Firebase', 'Redux'],
                'description': 'Developed cross-platform mobile app for task management with real-time synchronization, offline support, and collaborative features. Published on both iOS and Android app stores.'
            },
            {
                'name': 'AI-Powered Analytics Dashboard',
                'languages': ['Python', 'TensorFlow', 'D3.js', 'Flask'],
                'description': 'Created machine learning-powered analytics platform with interactive visualizations and predictive modeling capabilities. Processes 1TB+ of data daily.'
            },
            {
                'name': 'Open Source UI Library',
                'languages': ['TypeScript', 'React', 'Storybook', 'Jest'],
                'description': 'Developed and maintained popular open-source React component library with 5,000+ GitHub stars. Includes comprehensive documentation and testing suite.'
            }
        ],
        'interest_list': [
            'Machine Learning',
            'Open Source Contributing',
            'Rock Climbing',
            'Photography',
            'Chess',
            'Cooking',
            'Travel',
            'Blockchain Technology'
        ]
    }

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

@app.route('/generate_pdf_server', methods=['POST'])
def generate_pdf_server():
    """Server-side PDF generation as backup"""
    try:
        data = request.json
        user_data = data.get('user_data', {})
        html_content = data.get('html_content', '')
        css_content = data.get('css_content', '')
        
        # Create complete HTML document
        complete_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: 'Poppins', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background: white;
                }}
                .editable-content {{
                    background: transparent !important;
                    border: none !important;
                    padding: 0 !important;
                    box-shadow: none !important;
                }}
                .edit-controls {{
                    display: none !important;
                }}
                {css_content}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        return jsonify({
            'success': True,
            'html': complete_html,
            'filename': f"{user_data.get('name', 'Resume').replace(' ', '_')}.pdf"
        })
        
    except Exception as e:
        return jsonify({'error': f'Server PDF generation failed: {str(e)}'}), 500
