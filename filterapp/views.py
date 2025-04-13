from django.shortcuts import render
from PIL import Image, ImageFilter, ImageOps
import os
from django.conf import settings

def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_file = request.FILES['image']
        filter_type = request.POST.get('filter').lower()

        # Save original image
        image_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        with open(image_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Open image
        img = Image.open(image_path).convert('RGB')  # ensure RGB mode

        # Apply selected filter
        if filter_type == 'gray':
            img = img.convert('L').convert('RGB')
        elif filter_type == 'sepia':
            sepia = img.copy()
            pixels = sepia.load()
            for y in range(sepia.height):
                for x in range(sepia.width):
                    r, g, b = pixels[x, y]
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
            img = sepia
        elif filter_type == 'poster':
            img = ImageOps.posterize(img, 3)
        elif filter_type == 'blur':
            img = img.filter(ImageFilter.GaussianBlur(radius=10))
        elif filter_type == 'edge':
            img = img.convert('L')  # convert to grayscale
            img = img.filter(ImageFilter.FIND_EDGES)
            img = img.convert('RGB')
        elif filter_type == 'solar':
            img = ImageOps.solarize(img, threshold=128)
        else:
            return render(request, 'upload.html', {'error': 'Invalid filter selected'})

        # Save filtered image
        filtered_filename = 'filtered_' + uploaded_file.name
        filtered_path = os.path.join(settings.MEDIA_ROOT, filtered_filename)
        img.save(filtered_path)

        return render(request, 'result.html', {
            'image_url': 'media/' + filtered_filename
        })

    return render(request, 'upload.html')