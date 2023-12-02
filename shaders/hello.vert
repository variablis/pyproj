#version 330

// uniform vec2 Pan;
//uniform float zz;
// uniform float Zoo;
// uniform vec2 mp;
uniform mat4 Mvp;

in vec2 in_vert;
in vec4 in_color;

out vec4 v_color;

void main() {
    // vec3 eye = vec3(0,0, -3);
    // vec3 center = vec3(0,0, 0.0);
    // vec3 up = vec3(0.0, 1.0, 0.0);

    // vec3 _f = normalize(center - eye);
    // vec3 _r = normalize(cross(up, _f));
    // vec3 u = cross(_f, _r);

    // mat4 view = mat4(
    //     vec4(_r, -dot(_r, eye)),
    //     vec4(u, -dot(u, eye)),
    //     vec4(-_f, -dot(_f, eye)),
    //     vec4(-Pan, 0.0, 1.0)
    // );

//   float zf = (Zoo+1)/10;

//     float r,l,t,b,f,n = 0;

//     l=-1/zf;
//     r=1/zf;
//     b=-1/zf;
//     t=1/zf;

//     n=-1;
//     f=1;

  
    
    // mat4 proj = mat4(
    //     vec4(2/(r-l), 0, 0, -(r+l)/(r-l)),
    //     vec4(0, 2/(t-b), 0, -(t+b)/(t-b)),
    //     vec4(0, 0, -2/(f-n), -(f+n)/(f-n)),
    //     vec4(0, 0, 0, 1.0)
    // );

    // Pass the color to the fragment shader
    v_color = in_color; //* zz;

    // Set the transformed position
    // gl_Position = proj* view * vec4(in_vert, 0.0, 1.0);
    gl_Position = Mvp * vec4(in_vert, 0.0, 1.0);
}
