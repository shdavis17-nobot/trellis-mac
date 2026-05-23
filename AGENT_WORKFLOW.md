# AGENT_WORKFLOW.md: AI-to-3D-Print Pipeline

> **ATTENTION FUTURE AGENTS:** Read this document carefully before attempting to generate 3D models for the user. This outlines the exact ADI-approved pipeline for converting 2D images into 3D-printable `.stl` files on Apple Silicon.

## 🛑 Hardware Constraints
- **Host OS:** macOS (Apple Silicon).
- **CUDA/Nvidia Tools:** DO NOT attempt to run tools like `Hunyuan3D-2`. They have hard-coded dependencies on `cupy-cuda12x` and `deepspeed` and will fail on macOS.
- **The Solution:** We exclusively use this repository (`trellis-mac`), which is an Apple Silicon (MPS) optimized port of Microsoft's TRELLIS.2 model.

## 🛠️ The Standard Operating Procedure

When the user provides an image and asks for a 3D mesh, execute these steps exactly in this order:

### Phase 1: AI Generation (Terminal)
The agent must execute the Trellis generation script in the background. It takes an image and outputs a raw `.glb` and `.obj`.

1. **Activate the environment and run the generator:**
   ```bash
   cd /Users/shawn/Projects/trellis-mac
   source .venv/bin/activate
   python generate.py <path_to_user_provided_image.png>
   ```
2. **Monitor the process:** This takes about ~5 minutes to compute the mesh and bake the PBR textures.
3. **Outputs generated:** `output_3d.glb` and `output_3d.obj`.

### Phase 2: Mesh Cleanup (Blender Background Script)
Generative AI creates extremely dense meshes (1.5M+ triangles) filled with non-manifold edges, intersecting geometry, and internal floating vertices. Bambu Studio will reject these models. You must automatically fix them.

1. **Execute the Voxel Remesher Script:**
   Do NOT use `blender-mcp` if it is unstable. Instead, use a background shell command to trigger the pre-written `fix_mesh.py` script.
   ```bash
   /Applications/Blender.app/Contents/MacOS/Blender --background --python /Users/shawn/Projects/trellis-mac/fix_mesh.py
   ```
2. **What this does:** 
   - Imports `output_3d.obj`.
   - Scales the object to 25cm (or whatever the user requests).
   - Runs a **1.5mm Voxel Remesh**. This acts like a shrink-wrap, mathematically destroying all internal geometry and creating a flawless, watertight outer shell (0 non-manifold edges).
   - Runs a **Decimate** modifier to crush the triangle count down to a slicer-friendly size (100k-200k triangles).
   - Exports `bigfoot_perfected.stl` (or dynamically rename it based on the prompt).

### Phase 3: The Human Handoff (Spike Cleanup)
Generative models often hallucinate sharp "spikes" or "webbing" (especially between arms/legs). Automated smoothing ruins the core texture (like fur).

1. **Instruct the User:**
   Tell the user that the watertight `.stl` is ready in the `trellis-mac` directory.
2. **Provide Sculpting Instructions:**
   Direct the user to open the `.stl` in Blender, switch to **Sculpt Mode**, and hold `Shift` (which activates the Smooth brush) to manually swipe away the spikes in 10 seconds. This is the industry-standard way to preserve surface detail while eliminating hallucinations.

---
**End of Workflow.** Follow this pipeline exactly to ensure a smooth, crash-free experience.
