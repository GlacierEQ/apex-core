import os
import glob

def run_synthesis():
    target_repo = os.getcwd()
    patch_dir = os.path.join(target_repo, ".apex_aborted_patches")
    
    if not os.path.exists(patch_dir):
        print("[APEX] No aborted patches found. Surgical Sync was 100% successful.")
        return

    patches = glob.glob(f"{patch_dir}/*.patch")
    if not patches:
        print("[APEX] No aborted patches found in directory.")
        return

    print(f"[APEX] AI SYNTHESIS ENGINE ACTIVE")
    print(f"[APEX] Found {len(patches)} structurally aborted branches requiring AI resolution.\n")

    for patch_file in patches:
        branch_name = os.path.basename(patch_file).replace('.patch', '')
        with open(patch_file, 'r') as f:
            patch_content = f.read()
            
        # Basic check to avoid massive dumps
        lines = patch_content.splitlines()
        if len(lines) > 500:
            print(f"[-] {branch_name} is too massive ({len(lines)} lines). Skipping for manual architectural review.")
            continue
            
        print(f"[+] Structuring AI resolution prompt for: {branch_name}")
        
        prompt_file = os.path.join(patch_dir, f"{branch_name}_AI_PROMPT.md")
        with open(prompt_file, 'w') as f:
            f.write(f"# APEX AI Synthesis Request: {branch_name}\n\n")
            f.write("## Directive\n")
            f.write("You are an APEX Synthesis Agent. The following git patch was aborted during an automated merge because of structural conflicts with the current `main` branch. Your objective is to read the intent of this patch, analyze the target files in the current workspace, and intelligently rewrite the files to incorporate the new logic perfectly without breaking existing syntax.\n\n")
            f.write("## The Aborted Patch\n")
            f.write("```diff\n")
            f.write(patch_content + "\n")
            f.write("```\n")
            
    print(f"\n[APEX] Synthesis prompts generated in {patch_dir}/")
    print("[APEX] To execute, feed these prompts to the Antigravity CLI or your active Agent.")

if __name__ == "__main__":
    run_synthesis()
