# Data Project: Data Analysis to Streamlit Web Application

<div style="display: flex; justify-content: center; align-items: center">
<img src="https://i.pinimg.com/originals/e4/d3/95/e4d395849317f98f2a418c0e10182b0d.gif" style="width: 50%">
</div>

## Objective | User Story
The Marketing Lead of KZ Laptop Trader Company found that revenue of the business had decreased significantly in the first quarter of year. CEO of the company also started raising concerns about the sales deduction. They decided to hire Data Analyst (me) to handle the situation.
* What is the key factor affecting laptop price?
<p>To answer the question we need extract key information from **data** that could not be provided by the company due to the database access issues. </p>
<p>We accepted such a challenge!</p>
<p>The final request was stated as following: 
<ul>
<li>Provide key metrics affecting laptop prices (in .pptx or jupyter notebook wih code samples)</li>
<li>Create recomendational system to extract laptop models that could be potentially purchased</li>
</ul>
</p>

## Stages
* Data Collection
* Data Organization
* Data Analysis
* Development

### Tools
<table>
  <tr>
    <td>Stage Step</td>
    <td>Tech Stack</td>
  </tr>
  <tr>
    <td>Data Collection</td>
    <td>requests, beautifulSoup4, assyncio</td>
  </tr>
  <tr>
    <td>Data Organization</td>
    <td>Pandas, Numpy</td>
  </tr>
  <tr>
    <td>Data Analysis</td>
    <td>seaborn, Plotly, matplotlib, pandas</td>
  </tr>
  <tr>
    <td>Development</td>
    <td>Streamlit, plotly, OpenAI</td>
  </tr>
</table>

## Data Collection
Before development and Data Analysis step, we are in high demand for data.
<p>It means that we need to collect it and save somewhere</p>
<p>Nowadays there are tons of methods how to extract information, using API, online web crawlers, etc. But to showcase our skills to requesters, I wanted to approach the problem using my exisiting knowledge in python packages enabling us to scrape data from websites</p>

#### BeautifulSoup
**Beautiful Soup** is a library that makes it easy to scrape information from web pages. It sits atop an HTML or XML parser, providing Pythonic idioms for iterating, searching, and modifying the parse tree.
<p>As a main website from where we will extract data is KZ Electronics Shop ("Belyi Veter").</p>
<p>To perform web scrapping, we need to 
<ul>
  <li>Make HTTP requests on URL</li>
  <li>Get inner HTML content</li>
  <li>Parse through the content tree to extract required information</li>
</ul>
<p>In more programmatical language, we made following steps:
  
**Setting Up Configuration**:

* Configures the logging format and level.
* Defines custom headers to mimic human interaction with the website and avoid being blocked.
  
  ![](https://github.com/dxmension/Data-project-laptop-analysis/blob/main/assets/5264826213891955301.jpg)
  
**Defining Asynchronous Function**
* request_with_retries(url, headers, session, retries=10)
    Makes HTTP requests with retries and exponential backoff to handle CAPTCHA and network issues.

  ![](https://github.com/dxmension/Data-project-laptop-analysis/blob/main/assets/5262702996809178717.jpg)
    
* parse_item_card(item)
    Parses an individual item card to extract laptop information such as ID, title, prices, specifications, and image link.

  ![](https://github.com/dxmension/Data-project-laptop-analysis/blob/main/assets/9af03364-0272-44dc-8596-d6d86e1b1734.jpg)
  
* parse_listing(url, session)
    Parses the listing page to extract all item cards and their information. Returns a list of dictionaries containing laptop information and the BeautifulSoup object of the page.


  
* get_next_page_url(soup)
    Finds the URL of the next page from the current page's HTML content.



  
* save_csv(product_list, name="laptops.csv")
    Saves the product list to a CSV file using pandas.



  

**Executing the Full Scraping Process**

execute_full_scraping(url): Orchestrates the full scraping process:
Initializes the starting URL and an empty list for laptops.
Opens an asynchronous session with ClientSession.
Logs the start time and initiates scraping up to a maximum of 100 pages.
For each page, it logs the page number, parses the listing page, extracts laptop information, and updates the URL to the next page.
Handles delays between requests using asyncio.sleep with a random interval to avoid being blocked.
If the next page URL is not found, it logs an error and stops.
Saves the collected data to a CSV file.
Logs the end time and total time taken for scraping.
</p>
