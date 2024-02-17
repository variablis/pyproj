#version 330


uniform sampler2D tex;

in vec2 uvCoord;
out vec4 outColor;

float pxRange = 4; // set to distance field's pixel range

float median(float r, float g, float b) {
    return max(min(r, g), min(max(r, g), b));
}

float screenPxRange() {
    vec2 unitRange = vec2(pxRange)/vec2(textureSize(tex, 0));
    vec2 screenTexSize = vec2(1.0)/fwidth(uvCoord);
    return max(0.5*dot(unitRange, screenTexSize), 1.0);
}

void main() {
    vec3 texel = texture(tex, uvCoord).rgb;
    float sd = median(texel.r, texel.g, texel.b);
    float screenPxDistance = screenPxRange()*(sd - 0.5);
    float opacity = clamp(screenPxDistance + 0.5, 0.0, 1.0);
    outColor = mix(vec4(0.3, 0.8, 0.8,0), vec4(0.3, 0.8, 0.8,1), opacity);
}
