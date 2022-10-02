

def scale_character(model_name: str, scale_factor: float):
    chrbnd = Binder(GAME_CHR_PATH / f"{model_name}.chrbnd.dcx", from_bak=True)
    anibnd = Binder(GAME_CHR_PATH / f"{model_name}.anibnd.dcx", from_bak=True)

    model = FLVER(chrbnd[f"{model_name}.flver"])  # ID 200
    model.scale(scale_factor)
    chrbnd[f"{model_name}.flver"].set_uncompressed_data(model.pack())
    print("Model (FLVER) scaled.")

    ragdoll_hkx = RagdollHKX(chrbnd[f"{model_name}.hkx"])  # ID 300
    ragdoll_hkx.scale(scale_factor)
    chrbnd[f"{model_name}.hkx"].set_uncompressed_data(ragdoll_hkx.pack())
    print("Ragdoll physics scaled.")

    skeleton_hkx = SkeletonHKX(anibnd[1000000])   # "Skeleton.HKX" or "Skeleton.hkx"
    skeleton_hkx.scale(scale_factor)
    anibnd[1000000].set_uncompressed_data(skeleton_hkx.pack())
    print("Skeleton scaled.")

    try:
        cloth_entry = chrbnd[700]
    except KeyError:
        # No cloth data.
        print("No cloth HKX found.")
    else:
        cloth_hkx = ClothHKX(cloth_entry)
        print(cloth_hkx.get_root_tree_string())
        cloth_hkx.scale(scale_factor)
        print(cloth_hkx.get_root_tree_string())
        cloth_entry.set_uncompressed_data(cloth_hkx.pack())
        print("Cloth physics scaled.")

    print("Scaling animations:")
    for entry_id, entry in anibnd.entries_by_id.items():
        if entry_id < 1000000:
            print(f"  Scaling animation {entry_id}... ", end="")
            animation_hkx = AnimationHKX(entry)  # "aXX_XXXX.hkx"
            animation_hkx.scale(scale_factor)
            entry.set_uncompressed_data(animation_hkx.pack())
            print("Done.")

    print("Writing BNDs...")
    chrbnd.write()
    anibnd.write()
    print("Scaling complete.")