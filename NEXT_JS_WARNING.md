# Why You're Seeing "No Next.js Version Detected"

This warning appears when tools search for Next.js in the root directory.

## ✅ This is Normal and Expected

Your project is correctly structured as a monorepo:
- **Next.js is NOT in the root** - it's in `main-frontend/`
- **Next.js dependencies are in** `main-frontend/package.json`
- **Root package.json is for orchestration only**

## 🎯 How to Use This Project

### Development
```bash
# Start both servers from root
npm run dev

# Or work on frontend only
cd main-frontend
npm run dev
```

### Deployment

If deploying to **Vercel**:
1. Make sure `vercel.json` points to `main-frontend/`
2. Or deploy directly from `main-frontend/` directory

If deploying to **other platforms**:
- Deploy the frontend from `main-frontend/` directory
- Deploy the backend from `backend/` directory

## 📁 Project Structure

```
greenwells/
├── package.json          # ← Orchestration (npm-run-all)
├── main-frontend/        # ← Next.js app is HERE
│   ├── package.json      # ← Next.js dependencies
│   └── .next/            # ← Next.js build
└── backend/              # ← Django app
    ├── manage.py
    └── requirements.txt  # ← Django dependencies
```

## 🔧 Fixing the Warning

This warning can come from:
1. **Vercel** - Make sure root directory setting is correct
2. **IDE** - Some extensions search for Next.js in root
3. **Build tools** - Should use `main-frontend/` directory

### Solution
The warning doesn't affect functionality. To eliminate it:
- Point your deployment tool to `main-frontend/` directory
- Or ignore the warning (it's a false positive)

## ✅ Your Setup is Correct

The warning doesn't mean anything is broken. Your project structure is correct for a monorepo with separate backend and frontend applications.
