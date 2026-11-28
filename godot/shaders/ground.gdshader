// The ground: grass and sand from the vertex colours, worn dirt painted in where the path mask says (every road, lane,
// door path and trail, drawn by tools/map/farhallow_plan.py), each with its greyscale detail, under the baked light.
// Paths are part of the ground, so they can never float, clip or leave a seam.
shader_type spatial;
render_mode cull_back, diffuse_lambert, specular_disabled;
uniform sampler2D light_map : source_color, filter_linear, hint_default_white;
uniform sampler2D path_mask : filter_linear, hint_default_black;
uniform sampler2D grass_detail : source_color, filter_linear_mipmap, repeat_enable;
uniform sampler2D path_detail : source_color, filter_linear_mipmap, repeat_enable;
uniform vec3 path_col = vec3(0.6, 0.48, 0.34);
void fragment() {
	float m = smoothstep(0.12, 0.8, texture(path_mask, UV).r);
	vec3 grass = COLOR.rgb * texture(grass_detail, UV2).rgb;
	vec3 dirt = path_col * texture(path_detail, UV2 * 1.15).rgb;
	ALBEDO = mix(grass, dirt, m) * texture(light_map, UV).rgb;
	ROUGHNESS = 1.0;
}
