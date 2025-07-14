import { supabase } from './supabaseClient';

export const uploadImage = async (file, bucket) => {
  const fileExt = file.name.split('.').pop();
  const fileName = `${Math.random()}.${fileExt}`;
  const filePath = `${fileName}`;

  try {
    const { error: uploadError } = await supabase.storage
      .from(bucket)
      .upload(filePath, file);

    if (uploadError) {
      throw uploadError;
    }

    const { publicURL, error: urlError } = supabase.storage
      .from(bucket)
      .getPublicUrl(filePath);

    if (urlError) {
      throw urlError;
    }

    return { success: true, publicUrl: publicURL };
  } catch (error) {
    return { success: false, error: error.message };
  }
};