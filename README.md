# OG Image Generator — GitHub Action

Generate beautiful Open Graph social preview images for your GitHub repositories. A **1280×640 PNG** perfect for social sharing on Twitter/X, LinkedIn, Slack, Discord, and iMessage.

## Features

- **Automatic** — detects your repo name, description, stars, and language
- **5 free templates** — Default, Gradient, Minimal, Bold, Dark
- **Premium templates** — custom brand colors with a license key
- **Zero config** — add to any workflow in 2 minutes
- **Fast** — generates in under 2 seconds
- **No external API keys needed**

## Usage

```yaml
name: Generate OG Image
on:
  push:
    branches: [main]

jobs:
  og-image:
    runs-on: ubuntu-latest
    steps:
      - uses: astra-intelligence/og-image-action@v1
```

### With custom options

```yaml
- uses: astra-intelligence/og-image-action@v1
  with:
    repo: ${{ github.repository }}
    template: bold
    output-path: .github/og-image.png
```

## Templates

| Template | Preview |
|----------|---------|
| `default` | Dark theme with blue accent (GitHub-inspired) |
| `gradient` | Slate blue with blue accent |
| `minimal` | Clean white background with black text |
| `bold` | Deep indigo with purple accent |
| `dark` | Pure black with green accent |

## Premium (Paid)

Get premium templates with **custom brand colors**:

1. Purchase a license key: https://grantshatz.gumroad.com/l/og-preview-api-license
2. Add it to your workflow:

```yaml
- uses: astra-intelligence/og-image-action@v1
  with:
    template: premium
    license-key: ${{ secrets.OG_LICENSE_KEY }}
  env:
    CUSTOM_BG: "#your-hex-bg"
    CUSTOM_ACCENT: "#your-hex-accent"
```

### What you get with Premium

- Custom background and accent colors
- "Premium" badge on generated images
- Priority support
- Commercial use license
- Lifetime access (no recurring fees)

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `repo` | No | `${{ github.repository }}` | Repository name (owner/repo) |
| `output-path` | No | `og-image.png` | Where to save the image |
| `template` | No | `default` | Template style |
| `license-key` | No | `""` | Premium license key from Gumroad |

## Outputs

| Output | Description |
|--------|-------------|
| `image-path` | Path to the generated OG image file |

## Complete Workflow Example

```yaml
name: Generate and Deploy OG Image
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  generate-og:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate OG Image
        id: og
        uses: astra-intelligence/og-image-action@v1
        with:
          template: gradient
          output-path: .github/social-preview.png
      
      - name: Commit OG Image
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add .github/social-preview.png
          git commit -m "Update social preview image" || echo "No changes"
          git push
```

## How it works

The action:
1. Fetches your repo info from the GitHub API
2. Generates a 1280×640 PNG with your repo name, description, and stats
3. Saves it as an artifact and outputs the path
4. You can commit it or use it in deployment workflows

## License

MIT — free for any use. Premium features require a license key.