import os

file_path = 'templates/store/home.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1 (with review count)
pattern1 = """                        <!-- Rating Badge -->
                        <div class="mb-2">
                            <span class="badge bg-success rounded-1 px-2 py-1">
                                {{ product.avg_rating|default:"4.5" }} <i class="bi bi-star-fill" style="font-size: 0.65rem;"></i>
                            </span>
                            <span class="text-muted ms-1" style="font-size: 0.85rem;">(8,421)</span>
                        </div>"""

replace1 = """                        <!-- Rating Badge, Brand & Colors -->
                        <div class="mb-2 d-flex flex-wrap align-items-center gap-1">
                            <span class="badge bg-success rounded-1 px-2 py-1">
                                {{ product.avg_rating|default:"4.5"|floatformat:1 }} <i class="bi bi-star-fill" style="font-size: 0.65rem;"></i>
                            </span>
                            <span class="text-muted ms-1" style="font-size: 0.85rem;">(8,421)</span>
                            {% if product.brand %}
                            <span class="badge bg-light text-dark border">{{ product.brand.brand_name }}</span>
                            {% endif %}
                        </div>
                        {% if product.colors.exists %}
                        <div class="mb-2 d-flex flex-wrap gap-1">
                            {% for color in product.colors.all|slice:":3" %}
                                <div class="rounded-circle border border-1 shadow-sm" style="width: 14px; height: 14px; background-color: {{ color.color_code }};" title="{{ color.color_name }}"></div>
                            {% endfor %}
                            {% if product.colors.all|length > 3 %}
                                <span style="font-size: 0.7rem; line-height: 14px;" class="text-muted">+{{ product.colors.all|length|add:"-3" }}</span>
                            {% endif %}
                        </div>
                        {% endif %}"""

# Pattern 2 (without review count)
pattern2 = """                        <!-- Rating Badge -->
                        <div class="mb-2">
                            <span class="badge bg-success rounded-1 px-2 py-1">
                                {{ product.avg_rating|default:"4.5" }} <i class="bi bi-star-fill" style="font-size: 0.65rem;"></i>
                            </span>
                        </div>"""

replace2 = """                        <!-- Rating Badge, Brand & Colors -->
                        <div class="mb-2 d-flex flex-wrap align-items-center gap-1">
                            <span class="badge bg-success rounded-1 px-2 py-1">
                                {{ product.avg_rating|default:"4.5"|floatformat:1 }} <i class="bi bi-star-fill" style="font-size: 0.65rem;"></i>
                            </span>
                            {% if product.brand %}
                            <span class="badge bg-light text-dark border">{{ product.brand.brand_name }}</span>
                            {% endif %}
                        </div>
                        {% if product.colors.exists %}
                        <div class="mb-2 d-flex flex-wrap gap-1">
                            {% for color in product.colors.all|slice:":3" %}
                                <div class="rounded-circle border border-1 shadow-sm" style="width: 14px; height: 14px; background-color: {{ color.color_code }};" title="{{ color.color_name }}"></div>
                            {% endfor %}
                            {% if product.colors.all|length > 3 %}
                                <span style="font-size: 0.7rem; line-height: 14px;" class="text-muted">+{{ product.colors.all|length|add:"-3" }}</span>
                            {% endif %}
                        </div>
                        {% endif %}"""

content = content.replace(pattern1, replace1)
content = content.replace(pattern2, replace2)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Replaced content in home.html')
