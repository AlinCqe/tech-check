# Website Technologies Scraper

This is my solution for the Website Technologies Scraper challenge.


## Results

The first complete version of the workflow can be found in commit 24947f6.
On the 200 domains it found:

- 1,198 total detections;
- 149 unique technologies.

After adding WordPress plugin and theme detection, the result before name
normalization was:

- 1,561 total detections;
- 369 unique technologies.

And after normalization:

- 1555 total detections;
- 354 unique technologies.

total_detections counts every website-technology pair. If WordPress is found
on 10 websites, that means 10 detections. unique_technologies counts
WordPress only once.

## How I started

I first used requests and BeautifulSoup to collect every JavaScript src
found in the HTML:

```python
for script in soup.find_all("script", src=True):
    file.write(script["src"] + "\n")
```

And then made a very vague verification of how many techs i could find here, by prompting the file to chat gpt
and i got around 200 techs, incluing plugins or themes from techs

The first solution i thouhg was with a big file, with many technologies, and a  pattern for each
But didnt liked the part of a enormeus file

After checking more the pages, i saw in dev tools the Sources window, were the tech stack was arranged so cool, with folders
so i tried to group the URLs by their path structure. This worked for cases such
as /wp-content/plugins/..., but for other hundreds of technologies, i couldnt know when will the tech name came, and save it,
and the soltion ended in the same path, a big file with patterns

While researching how other projects solved this, i found Richard Penman's
builtwith repo (https://github.com/richardpenman/builtwith) . It uses an 
`apps.json` file containing technologies and regex patterns. 
After taking a look, i convinced myself that this is the solution

And also, after reading over and over the task page, i noticed that one of the debate topics, can lead directly to this  solution:
 - how would you discover new technologies in the future?

I read and adapted the logic in his project, changing
the collection part to Playwright, removed parts i did not need, made the code
more explicit, added more detection sources and saved proof for result.

## What the script collects

For every domain, Playwright collects:

- initial and final URL;
- response status and headers;
- raw HTML returned by the server;
- rendered HTML after JavaScript runs;
- script tags;
- link tags;
- meta tags;
- network requests made by the page.

The same Chromium browser is reused for all domains, but with a new context between websites.

## Technology detection

The detector checks the patterns from `apps.json` against:

- the final URL;
- response headers;
- raw and rendered HTML;
- meta tags;
- script URLs from the page and network requests.
- Wordpress resources(plugins or themes)


The script extracts the plugin or theme name from script tags, link tags and
network requests. `wordpress_components.json` maps known names to readable
product names. Unknown names are still saved as WordPress plugins or themes.

Only the first proof found for a technology is stored. urls are sanitized by
removing query parameters and fragments, because found some that contained API keys and
Set-Cookie values are also redacted.

## Output

The result is written to `results.json`:

```json
{
  "link": "example.com",
  "technologies": {
    "WordPress": {
      "proof": {
        "source": "html",
        "matched": "wp-content"
      }
    }
  }
}
```

## Run

```powershell
pip install -r requirements.txt
playwright install chromium
python main.py
```



## Current problems and what I would improve

Current code uses playwright, to scrape a lot of data, but most of it isnt being used. 

In the main file, we store in memory, every page and its tech data, and only writes in file once all the pages are finished, doing a bulk of 10k+ rows written

In a production project, to save resources, we could start with only html request, and then based of some rules, decide if we should use a more expensive request.
We could test it with 200 domains, and compare how mane detections appeared from html, network request..., and try to see patterns for example:
 -when html has to little links or meta data, network requests gave more information about tech stack?

aside from this cases, if the page returns a test page, or a empty page, or something like a anti bot page, ofc we go with something like playwright

the rules also depends heavly on the project scope, and what we focus more on, saving resources? or we dont care that much about resources, and focus more on detecting everything on the page

The script is tied to a app.json file with fingerprints, if a new tech is used by a website,
but isnt in the file, it wont be detected.

Only the home page is checked. 

Some domains fail when trying to connect, current version just notes as no technologies detected.




## How i would scale it to millions of domains

I would not start Playwright for every website but make a rule based progress

Start with a cheap request, if we consider we got enough data, good,
if based on some rules, we consider we could scrape more, we would go with smthing like playwright, to get more data

The question now is, how we establisehd those rules,
As i wrote in up there, we can run some test, on for example 200 pages, and compare the results we got, like how many techs we detected from html, and how many from network requests.

Then tryng to find those edges cases, where maybe we got only 3 techs from the html, and then 20 from network request, how does the html look? how many src link it has? is any frame work like NEXTJS present in all of those edge cases?

The rules would be also affected by the scope of the project, what we prioritirize more, resources, or data.



For anti bot measures, we could jump to playwright, with out much logic in the rules.




## How I would discover new technologies

I would save pieces of information (scr scipts, headers, meta etc), that werent noted as tech
and save them somewhere

If the same unknown piece of information appears on at least in three unrelated
websites, we could use a LLM that search what the domain belongs
to and propose a technology and regex rule for it

But this solution lets and empy, hole, those first 3 pages to show up with that tech, would have been not detected.
So, we could save those links, in a format like

{url: "http......",
links:[
  "http1...",
  "http2..."
]
meta: [
"ex1",
"ex2"
]
}

and every certain amount of time, we recheck this file, with the new rules, maybe every time a new technology is discovered, 
run a check here, so that way we dont check with the entire file again.


## Files

- `main.py` runs the scraper and writes the result
- `extract.py` collects data with playwright
- `get_techs.py` detects technologies
- `helpers.py` contains loading, WordPress extraction and sanitization helpers
- `apps.json` contains the general fingerprints
- `wordpress_components.json` normalizes WordPress component names
- `results.json` contains the output for the provided domains.

