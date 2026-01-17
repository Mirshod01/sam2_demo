# Quick Deployment Guide

## 🚀 Tez Setup (5 daqiqa)

### 1. GitHub Secrets qo'shish

Repository → Settings → Secrets and variables → Actions → New repository secret

Quyidagi secretlarni qo'shing:

| Secret Name | Value | Qayerdan topish |
|-------------|-------|----------------|
| `VASTAI_HOST` | `123.45.67.89` | Vast.ai dashboard → SSH button → IP address |
| `VASTAI_USERNAME` | `root` | Odatda `root` |
| `VASTAI_PORT` | `12345` | Vast.ai dashboard → SSH button → Port raqami |
| `VASTAI_SSH_KEY` | `-----BEGIN RSA PRIVATE KEY-----...` | `cat ~/.ssh/id_rsa` (local kompyuteringizda) |

### 2. Vast.ai serverda SSH key setup

```bash
# Local kompyuterda public key ni ko'chirish
cat ~/.ssh/id_rsa.pub

# Vast.ai serverga SSH orqali kirish
ssh root@<vast-ip> -p <port>

# Public key ni authorized_keys ga qo'shish
mkdir -p ~/.ssh
echo "PASTE_YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. Birinchi marta deploy qilish

Vast.ai serverda:

```bash
# Repository ni clone qilish
cd /workspace
git clone git@github.com:Mirshod01/sam2_demo.git
cd sam2_demo

# Deploy scriptini ishga tushirish
chmod +x deploy.sh
./deploy.sh
```

### 4. Avtomatik deployment test qilish

Local kompyuterda:

```bash
# O'zgarish kiritish
echo "# Test" >> README.md

# Commit va push
git add .
git commit -m "Test auto-deployment"
git push origin main
```

GitHub → Actions tabni oching va deployment jarayonini kuzating.

## ✅ Deploy muvaffaqiyatli bo'ldimi?

1. GitHub Actions → Deploy to Vast.ai Server → ✓ yashil belgini ko'ring
2. Vast.ai serverga SSH qiling:
   ```bash
   ssh root@<vast-ip> -p <port>
   cd /workspace/sam2_demo
   git log -1  # Oxirgi commit ko'rinishi kerak
   ```
3. Browser da ochish: `http://<vast-ip>:5000`

## 🔧 Muammolar va yechimlar

### "Permission denied (publickey)" xatosi

**Sabab:** SSH key to'g'ri o'rnatilmagan

**Yechim:**
```bash
# Local kompyuterda
cat ~/.ssh/id_rsa.pub

# Vast.ai serverda
echo "PASTE_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### "Could not resolve host" xatosi

**Sabab:** Vast.ai IP address noto'g'ri yoki server o'chirilgan

**Yechim:** Vast.ai dashboardda IP va Port ni qayta tekshiring

### Backend ishlamayapti

**Yechim:**
```bash
# Vast.ai serverda
cd /workspace/sam2_demo
python3 demo/backend/server/app.py

# Xatolarni ko'rish
```

### Dependencies o'rnatilmadi

**Yechim:**
```bash
# Vast.ai serverda
pip install --upgrade -r requirements.txt  # agar mavjud bo'lsa
# yoki
pip install flask flask-cors strawberry-graphql[flask] opencv-python numpy
```

## 📝 Har safar deploy jarayoni

1. **Local:** Kod yozish
2. **Local:** `git push origin main`
3. **GitHub Actions:** Avtomatik deploy boshlanadi
4. **Vast.ai:** Kod update bo'ladi, dependencies o'rnatiladi, restart bo'ladi
5. **Browser:** Yangi versiya ishlaydi! ✨

## 🎯 Next Steps

- [ ] SSL/HTTPS sozlash (Nginx + Let's Encrypt)
- [ ] Custom domain ulash
- [ ] Environment variables (.env) sozlash
- [ ] Monitoring qo'shish (PM2, systemd)
- [ ] Backup strategiyasi

## 📞 Yordam kerakmi?

- GitHub Issues: [Issues](https://github.com/Mirshod01/sam2_demo/issues)
- README: Batafsil ma'lumot uchun
