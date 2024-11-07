import http.cookiejar
import urllib.request

from lxml import html, etree # parse through HTML page returned from HTTP req

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
r = opener.open("https://www.risingstarchess.com/upcoming-tourney")

# Read the content of the response
content = r.read()

# Save the content to a text file
with open("response.txt", "wb") as file:
    file.write(content)

print("Response saved to response.txt")


# Read the saved HTML response
with open('response.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# Parse the HTML content
tree = html.fromstring(content)

# Extract all h2 elements
h2_elements = tree.xpath('//h2')

# Create a new HTML document with only the h2 elements
new_tree = etree.Element('html')
body = etree.SubElement(new_tree, 'body')
for h2 in h2_elements:
    body.append(h2)

# Convert the new tree to a string
new_content = etree.tostring(new_tree, pretty_print=True, encoding='unicode')

# Save the new content to a new file
with open('filtered_response.html', 'w', encoding='utf-8') as file:
    file.write(new_content)

print("Filtered response saved to filtered_response.html")

# Read the saved HTML file
with open('filtered_response.html', 'r', encoding='utf-8') as file:
    content = file.read()

# Parse the HTML content
tree = html.fromstring(content)

# Find all h2 elements
h2_elements = tree.xpath('//h2')

# Create a list to hold the tuples
tournaments = []

# Extract tournament name, date, and link
for h2 in h2_elements:
    text = h2.text_content().strip()
    # Split the text to separate the date and name
    if '--' in text:
        date, name = text.split('--', 1)
    else:
        continue

    # Extract the link if available
    link_element = h2.xpath('.//a/@href')
    link = link_element[0] if link_element else None

    # Add the tuple to the list
    tournaments.append((name.strip(), date.strip(), link))

for element in tournaments:
    print(element)
    print("\n")
