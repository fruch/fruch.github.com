# Blog Modernization Plan

## 1. Current State Audit

### Technology Stack

| Component | Current | Status |
|-----------|---------|--------|
| Framework | Jekyll-Bootstrap v0.2.13 | **Outdated** – Jekyll-Bootstrap was last maintained ~2013 |
| Jekyll version | GitHub Pages default (implicit) | **No Gemfile** – no pinned version, no local dev parity |
| Theme | `the-program` | **Legacy** – IE conditional comments, LESS-based CSS, no responsive design |
| CSS | LESS (compiled to a single `style.css`) | **Outdated** – LESS tooling is stale, no CSS variables |
| Syntax highlighting | Rouge (configured) / Pygments flag still present | Minor config debt |
| Comments | Disqus | Functional but increasingly ad-heavy |
| Analytics | Google Analytics (UA-based `tracking_id`) | **Broken** – Universal Analytics was sunset July 2024; needs GA4 |
| Feed | Atom + FeedBurner | FeedBurner is effectively unmaintained |
| CI/CD | None – relies on GitHub Pages auto-build | No preview builds, no checks |
| Build tooling | `Rakefile` (Ruby) | Rake commands use pre-1.0 Jekyll CLI syntax (`jekyll --auto --server`) |
| Content | 16 posts (2012–2022) | Stale – no posts in 3+ years; About page is placeholder |
| Assets | HTTP links to CDN scripts (modernizr, twitter widgets) | **Insecure** – uses `http://` instead of `https://` |
| Fonts | Ubuntu Mono via theme | Limited typography choices |
| Icons | Bootstrap 2 Glyphicons | **Outdated** – Bootstrap 2 is end-of-life |

### Key Problems

1. **Jekyll-Bootstrap is abandoned.** The framework has not been updated since 2013. It adds an abstraction layer (`JB/setup`, `JB/analytics`, etc.) that modern Jekyll no longer needs.
2. **No `Gemfile`.** Without one, there is no reproducible local build, and dependency versions are unpinned.
3. **IE conditional comments and legacy JS.** The theme still includes workarounds for IE 6–8, iOS orientation-change hacks, and loads Modernizr 2.0.6 – none of which are relevant today.
4. **Google Universal Analytics is dead.** The `UA-123-12` tracking ID stopped processing data in July 2024.
5. **HTTP links.** External script/link tags use `http://` which causes mixed-content warnings on HTTPS pages.
6. **No CI/CD pipeline.** No automated builds, no link checking, no preview deployments for PRs.
7. **About page is a placeholder.** The main biographical page says "TBD."
8. **Stale content.** The last post is from June 2022.

---

## 2. Version & Dependency Upgrades

### 2.1 Add a `Gemfile` for Reproducible Builds

```ruby
source "https://rubygems.org"

gem "github-pages", group: :jekyll_plugins
gem "jekyll-feed"
gem "jekyll-seo-tag"
gem "jekyll-sitemap"
gem "jekyll-paginate"
```

This pins the exact Jekyll version that GitHub Pages uses and adds commonly needed plugins.

### 2.2 Update `_config.yml`

- Remove the `pygments: true` line (deprecated; `highlighter: rouge` is already set).
- Remove `auto: true` (replaced by `--watch` in modern Jekyll).
- Add `plugins:` section for the new gems.
- Migrate analytics to GA4 (measurement ID `G-XXXXXXXXXX`) or remove analytics entirely.
- Update `production_url` from `http://` to `https://`.
- Add SEO-related fields (`description`, `url`, `baseurl`, `locale`, `social` links).

### 2.3 Update `Rakefile` or Replace It

The `Rakefile` uses legacy Jekyll CLI syntax. Options:

- **Option A (minimal):** Update `rake preview` to use `bundle exec jekyll serve --livereload`.
- **Option B (recommended):** Drop the `Rakefile` entirely and document `bundle exec jekyll serve` in the README. Post creation can be done by hand or with a simple shell alias.

---

## 3. Visual / Design Revamp

### 3.1 Theme Migration

**Recommended approach:** Replace `the-program` + Jekyll-Bootstrap with a modern, maintained Jekyll theme.

Top candidates (all free, GitHub Pages compatible, actively maintained):

| Theme | Highlights |
|-------|-----------|
| [**Minimal Mistakes**](https://github.com/mmistakes/minimal-mistakes) | Feature-rich, responsive, dark mode, SEO, wide community |
| [**Chirpy**](https://github.com/cotes2020/jekyll-theme-chirpy) | Clean dev-blog style, TOC sidebar, dark/light mode, search |
| [**Just the Docs**](https://github.com/just-the-docs/just-the-docs) | If the blog also needs documentation pages |

**Recommendation:** **Minimal Mistakes** or **Chirpy** – both are well-documented, mobile-friendly, and support tag/category archives out of the box.

### 3.2 What the New Theme Should Provide

- **Responsive design** – mobile-first layout
- **Dark / light mode toggle**
- **Modern typography** – system font stack or web-safe variable fonts
- **Proper `<meta>` and Open Graph tags** for social sharing (handled by `jekyll-seo-tag`)
- **Built-in search** (Chirpy has Lunr.js search; Minimal Mistakes supports Algolia or Lunr)
- **Tag and category archive pages** generated automatically
- **Reading-time estimates** on posts
- **Table of contents** sidebar for longer posts
- **Syntax-highlighted code blocks** with copy button

### 3.3 Migration Steps

1. Install the chosen theme as a Ruby gem (or remote theme).
2. Remove `_includes/JB/`, `_includes/themes/`, `assets/themes/` directories.
3. Update every post/page front matter:
   - Remove `{% include JB/setup %}` lines.
   - Ensure `layout:`, `title:`, `tags:`, `categories:` are present.
4. Move images from `assets/img/` to a path the new theme expects (usually the same or `assets/images/`).
5. Configure the new theme in `_config.yml` (author info, social links, navigation, etc.).
6. Test locally with `bundle exec jekyll serve`.

---

## 4. Content Revamp

### 4.1 About Page

The current About page (`about.md`) is a placeholder. It should be rewritten to include:

- A professional bio (2–3 paragraphs): background, current role, areas of expertise.
- Links to GitHub, LinkedIn, Twitter/X, and any speaking/conference profiles.
- Optionally a professional headshot or avatar.

### 4.2 Homepage

The current homepage (`index.md`) shows only the last 4 posts with a casual intro. Modernize it to:

- Show a brief author intro / hero section.
- Display recent posts with excerpts (not just titles).
- Optionally feature "pinned" or "popular" posts.

### 4.3 Existing Posts Cleanup

- **Review all 16 posts** for broken links (Twitter links may be broken since the rebrand to X, Travis CI links may be dead).
- Fix any image paths that break during theme migration.
- Add `excerpt` or `description` front matter to posts that lack it, for better SEO and social previews.
- Consider adding `last_modified_at` dates for SEO.

### 4.4 New Content Ideas

Given the blog's history (Python, DevOps, CI/CD, conferences), potential new posts:

- Reflections on how the tooling landscape changed since 2012.
- A "blog reboot" post explaining the modernization.
- Updated thoughts on GitHub Actions (the 2020 post is popular).
- ScyllaDB / database topics from professional experience.

### 4.5 Navigation

Add a clear, consistent navigation bar:

- Home
- Blog / Archive
- Tags
- About
- (Optional) Projects / Talks

Remove the "py Ammo." link if the page is no longer relevant, or update it.

---

## 5. CI/CD & Infrastructure

### 5.1 GitHub Actions Workflow

Create `.github/workflows/pages.yml`:

```yaml
name: Deploy Jekyll site to GitHub Pages

on:
  push:
    branches: ["master"]
  pull_request:
    branches: ["master"]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.3'
          bundler-cache: true
      - name: Build with Jekyll
        run: bundle exec jekyll build
        env:
          JEKYLL_ENV: production
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3

  deploy:
    if: github.ref == 'refs/heads/master'
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 5.2 Additional CI Checks (Optional)

- **HTML Proofer** – validates links, images, and HTML in the built site.
- **Markdown lint** – catches formatting issues in posts.
- **PR preview deployments** – using a Netlify or Cloudflare Pages preview, or GitHub Pages preview environments.

---

## 6. Recommended Migration Path

### Phase 1 – Foundation (1–2 days)

- [ ] Add `Gemfile` and `Gemfile.lock`
- [ ] Clean up `_config.yml` (remove deprecated options, fix URLs to HTTPS)
- [ ] Add GitHub Actions workflow for build & deploy
- [ ] Verify the site builds and deploys as-is before changing the theme

### Phase 2 – Theme Migration (2–3 days)

- [ ] Choose and install new theme (Minimal Mistakes or Chirpy)
- [ ] Migrate layouts and remove Jekyll-Bootstrap scaffolding (`_includes/JB/`, `_includes/themes/`, `assets/themes/`)
- [ ] Update all posts to remove `{% include JB/setup %}` lines
- [ ] Configure new theme settings (navigation, author, social links, colors)
- [ ] Test on mobile and desktop

### Phase 3 – Content Refresh (1–2 days)

- [ ] Rewrite the About page with a proper bio
- [ ] Update the homepage with a modern layout (hero, excerpts, featured posts)
- [ ] Audit all posts for broken links and fix them
- [ ] Add descriptions/excerpts to posts missing them
- [ ] Write a "Blog Reboot" post announcing the refresh

### Phase 4 – Polish & Extras (1 day)

- [ ] Add `jekyll-seo-tag` and `jekyll-sitemap` for SEO
- [ ] Set up GA4 analytics (or remove analytics)
- [ ] Replace Disqus with a lighter alternative (giscus, utterances) or remove comments
- [ ] Add a proper RSS/Atom feed via `jekyll-feed`
- [ ] Update `README.md` with development setup instructions
- [ ] Final cross-browser and mobile testing

---

## 7. Summary of Key Decisions Needed

| Decision | Options | Recommendation |
|----------|---------|----------------|
| Theme | Minimal Mistakes / Chirpy / Other | **Chirpy** – clean dev-blog aesthetic, built-in search and dark mode |
| Comments | Disqus / giscus / utterances / None | **giscus** – GitHub Discussions-based, no ads, lightweight |
| Analytics | GA4 / Plausible / None | **None** or **Plausible** – privacy-friendly; GA4 if tracking is important |
| Deployment | GitHub Pages auto / GitHub Actions | **GitHub Actions** – more control, can add build checks |
| Feed | FeedBurner / jekyll-feed | **jekyll-feed** – native, no third-party dependency |
