# Fruch's Blog

A personal blog powered by [Jekyll](https://jekyllrb.com/) and hosted on [GitHub Pages](https://pages.github.com/).

## Quickstart

### Prerequisites

You need **Ruby** (>= 2.7) and **Bundler** installed.

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install ruby-full build-essential zlib1g-dev
gem install bundler
```

#### macOS

Ruby is pre-installed on macOS. If you need a newer version, use [Homebrew](https://brew.sh/):

```bash
brew install ruby
gem install bundler
```

Make sure the Homebrew Ruby is on your `PATH`. Add this to your `~/.zshrc` or `~/.bash_profile`:

```bash
export PATH="/opt/homebrew/opt/ruby/bin:$PATH"
```

#### Windows

Install Ruby using [RubyInstaller](https://rubyinstaller.org/) (choose the version **with DevKit**). After installation, run:

```cmd
gem install bundler
```

### Install Dependencies

Clone the repository and install the required gems:

```bash
git clone https://github.com/fruch/fruch.github.com.git
cd fruch.github.com
bundle install
```

### Preview the Blog Locally

```bash
bundle exec jekyll serve --livereload
```

Or use the Rake task:

```bash
rake preview
```

The site will be available at **http://localhost:4000**. Changes to files are automatically detected and the browser will refresh.

### Build the Site

To generate the static site without starting a server:

```bash
bundle exec jekyll build
```

The output is written to the `_site/` directory.

## Creating a New Post

```bash
rake post title="My New Post"
```

This creates a new Markdown file in `_posts/` with the correct front matter.

## Deployment

The site is automatically built and deployed to GitHub Pages via a [GitHub Actions workflow](.github/workflows/pages.yml) on every push to `master`.

## License

[Creative Commons](https://creativecommons.org/licenses/by-nc-sa/3.0/)
