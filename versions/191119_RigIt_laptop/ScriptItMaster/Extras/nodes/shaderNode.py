shader = pm.shadingNode("lambert", asShader=True, n=name + "_lambert")

# input attributes:
shader.c  # c = color
shader.transparency
# output attributes:
shader.oc  # oc = outColor
shader.ocr  # ocr = outColorR
shader.outTransparency
