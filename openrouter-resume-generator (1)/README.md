# Enhanced OpenRouter AI Resume Generator

A comprehensive resume generator with dynamic lists, profile photos, section toggles, and AI-powered content editing.

## 🆕 New Features

### Dynamic Lists Management
- ✅ **Education**: Course name, university, duration, SGPA/percentage
- ✅ **Skills**: Categorized skills (Technical, Soft, Languages, Other)
- ✅ **Experience**: Job role, organization, duration, description
- ✅ **Projects**: Name, technologies/languages, description
- ✅ **Interests**: Individual interest items

### Profile Photo Management
- ✅ Upload profile photos (PNG, JPG, JPEG, GIF)
- ✅ Preview and remove functionality
- ✅ Toggle show/hide on resume

### Section Control
- ✅ Show/hide toggles for all resume sections
- ✅ Professional summary toggle
- ✅ Dynamic section rendering

### Inline Editing
- ✅ Click-to-edit AI-generated content
- ✅ Save, cancel, and regenerate options
- ✅ Real-time content updates
- ✅ No full regeneration needed

### Enhanced UX
- ✅ Language selector for projects
- ✅ Improved form validation
- ✅ Better responsive design
- ✅ Enhanced error handling

## 🚀 Quick Start

1. **Install Dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

2. **Run the Application**
   \`\`\`bash
   python run.py
   \`\`\`

3. **Access the App**
   - Main App: http://localhost:5000
   - Admin Panel: http://localhost:5000/admin
   - Default Admin: `admin` / `admin123`

4. **Configure OpenRouter API**
   - Get your API key from [OpenRouter Dashboard](https://openrouter.ai/keys)
   - Login to admin panel and update the API key

## 📋 How to Use

### Creating a Resume

1. **Personal Information**: Fill in basic details
2. **Profile Photo**: Upload and toggle visibility
3. **Education**: Add multiple education entries
4. **Skills**: Categorize your skills
5. **Experience**: Add work experience entries
6. **Projects**: Select technologies and describe projects
7. **Interests**: Add personal interests
8. **Section Toggles**: Choose which sections to show
9. **Generate**: Click to create AI-powered resume
10. **Edit**: Click on AI content to edit inline
11. **Download**: Save as PDF

### Inline Editing

- Click any highlighted AI-generated content
- Edit directly in the preview
- Use controls to:
  - **Save**: Keep your changes
  - **Cancel**: Discard changes
  - **Regenerate AI**: Get new AI content

### Dynamic Lists

- Use **Add** buttons to create new entries
- Click **×** to remove items
- All lists maintain at least one item
- Form validates required fields

## 🎨 Customization

### Adding Languages for Projects
Edit the language tags in the JavaScript section of `templates/index.html`:

\`\`\`javascript
<span class="language-tag" data-lang="YourLanguage">YourLanguage</span>
\`\`\`

### Custom Skill Categories
Modify the skill category options in the form:

\`\`\`html
<option value="YourCategory">Your Category</option>
\`\`\`

## 🔧 Technical Details

### Database Schema
- **templates**: Resume templates with HTML/CSS
- **settings**: Configuration including API keys
- **admin_users**: Admin authentication
- **user_resumes**: Draft resume storage (optional)

### File Structure
\`\`\`
├── app.py                 # Main Flask application
├── run.py                 # Application runner
├── requirements.txt       # Dependencies
├── resume_generator.db    # SQLite database
├── templates/             # HTML templates
├── static/
│   ├── profile_photos/    # Uploaded profile photos
│   └── uploads/           # Other uploads
\`\`\`

### API Endpoints
- `POST /generate_resume` - Generate resume with AI
- `POST /upload_profile_photo` - Upload profile photo
- `POST /update_ai_content` - Regenerate specific content
- `GET /get_templates` - Fetch available templates

## 🛡️ Security Features

- Password hashing for admin accounts
- File type validation for uploads
- SQL injection prevention
- XSS protection
- Session-based authentication
- Secure file handling

## 🐛 Troubleshooting

### Common Issues

1. **Photo Upload Fails**
   - Check file size (max 16MB)
   - Ensure valid image format
   - Verify upload directory permissions

2. **AI Content Not Generating**
   - Verify OpenRouter API key
   - Check account balance
   - Ensure internet connection

3. **Inline Editing Not Working**
   - Check JavaScript console for errors
   - Ensure html2pdf.js is loaded
   - Try refreshing the page

## 📈 Performance

- Optimized for large forms with many list items
- Efficient AI API usage
- Responsive design for all devices
- Fast PDF generation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test all new features
4. Submit pull request

## 📄 License

MIT License - Free for personal and commercial use.

---

**Enhanced with ❤️ for better resume creation experience!**
