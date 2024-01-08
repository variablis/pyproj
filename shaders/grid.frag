#version 330

uniform float opacity;

in vec4 v_color;
out vec4 f_color;

void main() {
    f_color = vec4(v_color.rgb, v_color.a * opacity);
}