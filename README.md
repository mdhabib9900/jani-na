# ProImage Studio

An advanced, professional image generator web tool powered by Pollinations.ai.

## Features
- Prompt + negative prompt workflow
- Pollinations image models (flux, turbo, gptimage, kontext, seedream, nanobanana)
- Size, output format, and seed controls
- Download generated results
- Uses `POLLINATIONS_API_KEY` automatically when set

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`.

## API key setup (optional but recommended)
```bash
export POLLINATIONS_API_KEY="your_key_here"
```

If no key is set, the app still calls Pollinations public endpoint without Authorization.


## Troubleshooting
- If image preview fails, the backend now validates Pollinations response type and returns a clear error when upstream sends non-image data.
- Check server logs and the API response `error`/`details` fields in browser dev tools.
