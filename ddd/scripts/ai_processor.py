import sys
import re
from typing import List
import os
from datetime import datetime

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

    # Download necessary NLTK data
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt_tab', quiet=True)  # Added this line
except ImportError:
    print("NLTK is not installed. Some features may not work properly.")
except LookupError:
    print("NLTK data is missing. Please run the following commands:")
    print("import nltk")
    print("nltk.download('punkt')")
    print("nltk.download('stopwords')")
    print("nltk.download('punkt_tab')")  # Added this line
    sys.exit(1)

def generate_tags(file_path: str) -> List[str]:
    """
    Generate tags for a given diary entry file.
    
    Args:
    file_path (str): Path to the diary entry file.
    
    Returns:
    List[str]: List of generated tags.
    """
    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Extract existing tags if any
    existing_tags = re.findall(r'#(\w+)', content)
    
    try:
        # Tokenize the content
        tokens = word_tokenize(content.lower())
        
        # Remove stopwords and punctuation
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
        
        # Count word frequencies
        word_freq = nltk.FreqDist(tokens)
        
        # Get the top 5 most frequent words as potential tags
        potential_tags = [word for word, _ in word_freq.most_common(5)]
    except NameError:
        print("NLTK functionality is not available. Using basic tag extraction.")
        potential_tags = []
    
    # Combine existing tags and potential tags, removing duplicates
    all_tags = list(set(existing_tags + potential_tags))
    
    return all_tags

def identify_sticky_entries(entries_dir: str = 'entries') -> List[str]:
    """
    Identify potential sticky entries based on content and metadata.
    
    Args:
    entries_dir (str): Directory containing diary entries.
    
    Returns:
    List[str]: List of file names for potential sticky entries.
    """
    sticky_entries = []
    for filename in os.listdir(entries_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(entries_dir, filename)
            with open(file_path, 'r') as file:
                content = file.read()
            
            # Check for indicators of importance
            if '#important' in content.lower() or '#sticky' in content.lower():
                sticky_entries.append(filename)
            
            # Check for number of tags (lowered threshold)
            tags = re.findall(r'#(\w+)', content)
            if len(tags) > 2:  # Lowered from 5 to 2
                sticky_entries.append(filename)
            
            # Check for length of entry
            if len(content.split()) > 100:  # Entries with more than 100 words
                sticky_entries.append(filename)
            
            # Check for presence of certain keywords
            important_keywords = ['important', 'crucial', 'significant', 'remember', 'key', 'vital', 'essential']
            if any(keyword in content.lower() for keyword in important_keywords):
                sticky_entries.append(filename)
    
    # If we still don't have at least 3 sticky entries, add the most recent ones
    if len(sticky_entries) < 3:
        all_entries = sorted([f for f in os.listdir(entries_dir) if f.endswith('.md')], reverse=True)
        sticky_entries.extend(all_entries[:3 - len(sticky_entries)])
    
    return list(set(sticky_entries))  # Remove duplicates

def update_homepage(entries_dir: str = 'entries', homepage_path: str = 'README.md'):
    """
    Update the homepage with recent entries, sticky entries, and tags.
    
    Args:
    entries_dir (str): Directory containing diary entries.
    homepage_path (str): Path to the homepage file (now README.md).
    """
    # Get sticky entries
    sticky_entries = identify_sticky_entries(entries_dir)
    
    # Get recent entries (last 5)
    all_entries = sorted([f for f in os.listdir(entries_dir) if f.endswith('.md')], reverse=True)
    recent_entries = all_entries[:5]
    
    # Collect all tags
    all_tags = set()
    for entry in all_entries:
        file_path = os.path.join(entries_dir, entry)
        entry_tags = generate_tags(file_path)
        all_tags.update(entry_tags)
    
    # Generate homepage content
    content = "# AI-Assisted Diary\n\n"
    
    content += "## Sticky Diaries\n"
    for entry in sticky_entries:
        content += f"- [{entry[:-3]}]({entries_dir}/{entry})\n"
    content += "\n"
    
    content += "## Chronicle Diaries\n"
    for entry in recent_entries:
        content += f"- [{entry[:-3]}]({entries_dir}/{entry})\n"
    content += "\n"
    
    content += "## Tagged Diaries\n"
    for tag in sorted(all_tags):
        content += f"- #{tag}\n"
    content += "\n"
    
    content += "## Search Window\n"
    content += "(Search functionality to be implemented)\n\n"
    
    content += "---\n\n"
    content += "Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Write to homepage file
    with open(homepage_path, 'w') as file:
        file.write(content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ai_processor.py <function_name> [arguments]")
        sys.exit(1)
    
    function_name = sys.argv[1]
    
    if function_name == "generate_tags":
        if len(sys.argv) != 3:
            print("Usage: python ai_processor.py generate_tags <file_path>")
            sys.exit(1)
        file_path = sys.argv[2]
        tags = generate_tags(file_path)
        print("Generated tags:", tags)
    
    elif function_name == "identify_sticky_entries":
        sticky_entries = identify_sticky_entries()
        print("Potential sticky entries:", sticky_entries)
    
    elif function_name == "update_homepage":
        update_homepage()
        print("Homepage updated successfully.")
    
    else:
        print(f"Unknown function: {function_name}")
        sys.exit(1)