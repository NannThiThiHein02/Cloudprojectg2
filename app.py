from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Color data
COLORS = [
    {"name": "Red", "hex": "#FF0000"},
    {"name": "Blue", "hex": "#0000FF"},
    {"name": "Green", "hex": "#00FF00"},
    {"name": "Yellow", "hex": "#FFFF00"},
    {"name": "Purple", "hex": "#800080"},
    {"name": "Primary", "hex": "#4F46E5"},
]

def initialize_votes():
    """Initialize votes in session if not present"""
    if 'votes' not in session:
        session['votes'] = {}

@app.route('/')
def index():
    """Main page displaying colors and voting results"""
    initialize_votes()
    
    # Calculate total votes and percentages
    votes = session.get('votes', {})
    total_votes = sum(votes.values()) if votes else 0
    
    percentages = {}
    for color in COLORS:
        color_name = color['name']
        vote_count = votes.get(color_name, 0)
        percentage = round((vote_count / total_votes) * 100, 1) if total_votes > 0 else 0
        percentages[color_name] = percentage
    
    return render_template(
        'index.html',
        colors=COLORS,
        votes=votes,
        total_votes=total_votes,
        percentages=percentages
    )

@app.route('/vote', methods=['POST'])
def vote():
    """Handle voting for a color"""
    color_name = request.form.get('color_name')
    
    if color_name:
        initialize_votes()
        votes = session.get('votes', {})
        
        # Increment vote count for the selected color
        votes[color_name] = votes.get(color_name, 0) + 1
        session['votes'] = votes
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)