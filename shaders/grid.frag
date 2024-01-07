#version 330

uniform float opacity;
out vec4 f_color;

void main() {
    f_color = vec4(0.0, 1, 0.3, .2*opacity);
}