import requests
import streamlit as st


# ---- Define Config ---- #
st.set_page_config(page_title="Mapping Out New York City Restaurants", page_icon=':house:', layout='wide')

#Use local css
def local_css(file_name):
	with open(file_name) as f:
		st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style/style.css")

# ---- Header Section ----#
with st.container():
	st.title("CSE 6242: Health Clusters in NYC Dining")
	st.write("""
          This Streamlit application shows an interactive map 🗺️ of New York City with the ability to dig into individual restaurants history and violations as recorded by the city. This can be viewed in both the form of a heatmap and hierarchical clusters that allow each restaurant to be drilled into. These two views provide a deeper understanding of health trends across the city.
          
          All data is publically available at [NYC Open Data](https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j/about_data). This data is updated on a daily basis, and new entries are pulled in on a daily basis to be appended to our data and mapped accordingly. With this application, you have access to health inspection results as they happen! Think of it like CrimeSpot, but for trying to avoid food poisoning!
          """)
     

# ---- Team Info ---- #
with st.container():
	st.write("---")
	st.subheader("Hi, we're Team 120 :wave:")
	st.write("Team 120 is composed of four group members. Here's a little about them!")
	st.write("- **Chris**: ML enthusiast solving the worlds problems one byte at a time.")
	st.write("- **Romain**: I like creating visualizations and insights (even if I'm an algebraist at heart!) and have technical expertise in finance and the travel industry. ")
	st.write("- **Suganya**: I am a data enthusiast who loves analytics and enjoys uncovering hidden trends and patterns with a background in Banking ")
	st.write("- **Zo**: I am a data scientist with a background in physics and astronomy. I believe that visualization is the key to helping people explore and understand complex datasets and I hope you enjoy this one!")
    
# ---- Contact ----#
with st.container():
	st.header("Contact Us")
	#Documentation: https://formsubmit.co/
	contact_form = """
	<form action="https://formsubmit.co/cromainbaker@gmail.com" method="POST">
		<input type="hidden" name="_captcha" value="false">
     		<input type="text" name="name" placeholder="Your name" required>
     		<input type="email" name="email" placeholder="Your email" required>
     		<textarea name="message" placeholder="Your message here" required></textarea>
     		<button type="submit">Send</button>
	</form>"""
	left_column, right_column = st.columns(2)
	with left_column:
		st.markdown(contact_form, unsafe_allow_html=True)
	with right_column:
		st.empty()
