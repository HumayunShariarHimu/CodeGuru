# CodeGuru

CodeGuru is a searchable directory of Bangla-first programming books and software-development guides. Each published project has its own GitHub repository and GitHub Pages reading site.

- **Live directory:** https://humayunshariarhimu.github.io/CodeGuru/
- **GitHub repository:** https://github.com/HumayunShariarHimu/CodeGuru
- **Maintainer:** Humayun Shariar Himu

The course descriptions and repository links are maintained in [`projects.json`](projects.json). The site build renders those records into the homepage as ordinary HTML so the directory remains readable to search crawlers and visitors without JavaScript. The optional search field filters the already-rendered cards in the browser.

## Build the Pages site

```sh
python -m pip install -r requirements-pages.txt
python scripts/build_hub.py
python scripts/build_pages.py --output _site
```

The GitHub Actions workflow runs both build scripts and publishes `_site` to GitHub Pages. The site uses the `/CodeGuru/` project-page path; generated canonical URLs, `robots.txt`, and `sitemap.xml` follow that path.

Course content remains subject to the license and attribution stated in each individual project repository. This directory does not replace or change those terms.
