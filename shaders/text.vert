#version 330

uniform mat4 mvp;

in vec2 in_pos;
in vec2 in_vert;
in vec2 tex_coord;

out vec2 uvCoord;

void main() {
    gl_Position = mvp* vec4(in_pos+in_vert, 0.0, 1.0);
    uvCoord = tex_coord;
}
