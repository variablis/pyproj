#version 330

layout (points) in;
layout (triangle_strip, max_vertices = 6) out;

uniform mat4 mvp;
uniform float zoomfact;
uniform float diameter = 0.65;

in vec4 v_color[];
out vec4 g_color;


void build_circle(vec4 position) {  
    float dz = diameter/zoomfact;

    gl_Position = mvp* (position + vec4(0.02*dz, 0.0*dz, 0.0, 0.0));   
    EmitVertex(); 
    gl_Position = mvp* (position + vec4(0.01*dz, 0.01732*dz, 0.0, 0.0));    
    EmitVertex();
    gl_Position = mvp* (position + vec4(0.01*dz, -0.01732*dz, 0.0, 0.0));  
    EmitVertex();
    gl_Position = mvp* (position + vec4(-0.01*dz, 0.01732*dz, 0.0, 0.0));    
    EmitVertex();
    gl_Position = mvp* (position + vec4(-0.01*dz, -0.01732*dz, 0.0, 0.0));  
    EmitVertex();
    gl_Position = mvp* (position + vec4(-0.02*dz, 0.0*dz, 0.0, 0.0));    
    EmitVertex();

    EndPrimitive();
}


void main() {

    g_color = v_color[0];

    build_circle(gl_in[0].gl_Position);

}