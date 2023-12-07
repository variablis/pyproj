#version 330


uniform sampler2D tex;

in vec2 uvCoord;
out vec4 outColor;

float median(float r, float g, float b) {
    return max(min(r, g), min(max(r, g), b));
}

float screenPxRange(sampler2D tex) {
    vec2 unitRange = vec2(6.0)/vec2(textureSize(tex, 0));
    vec2 screenTexSize = vec2(1.0)/fwidth(uvCoord);
    return max(0.5*dot(unitRange, screenTexSize), 1.0);
}

void main() {

    //vec2 inverteduvCoord = vec2(uvCoord.s, 1.0 - uvCoord.t);

    vec4 texel = texture(tex, uvCoord);
    

    float pxRange; 
    pxRange = screenPxRange(tex);

    float dist = median(texel.r, texel.g, texel.b);

    float pxDist = pxRange * (dist - 0.5);
    float opacity = clamp(pxDist + 0.5, 0.0, 1.0);

    outColor = vec4(0.3, 0.8, 0.8, opacity*texel.a);
}
