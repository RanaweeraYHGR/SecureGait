// supabaseImageUpload.js - A utility for uploading images to Supabase Storage

import { createClient } from '@supabase/supabase-js';

// Initialize the Supabase client
const supabaseUrl = 'https://ftioxcgnobztqbuyhihc.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ0aW94Y2dub2J6dHFidXloaWhjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjIwMTYsImV4cCI6MjA2NzM5ODAxNn0.7dcKOAL6-znVVIGXt5o2SJdNVVHm0MpZm152Gq34Ygw'; // Replace with your actual anon key
const supabase = createClient(supabaseUrl, supabaseAnonKey);

/**
 * Uploads an image file to Supabase Storage
 * @param {File} imageFile - The image file to upload
 * @param {string} bucketName - The storage bucket name
 * @param {string} folderPath - Optional folder path within the bucket
 * @returns {Promise} - Promise with upload result
 */
export async function uploadImage(imageFile, bucketName, folderPath = '') {
  try {
    // Create a unique file name
    const fileExt = imageFile.name.split('.').pop();
    const fileName = `${Date.now()}.${fileExt}`;
    const filePath = folderPath ? `${folderPath}/${fileName}` : fileName;

    // Upload the file to Supabase Storage
    const { data, error } = await supabase.storage
      .from(bucketName)
      .upload(filePath, imageFile, {
        cacheControl: '3600',
        upsert: false
      });

    if (error) {
      throw error;
    }

    // Get the public URL for the uploaded file
    const { data: publicUrlData } = supabase.storage
      .from(bucketName)
      .getPublicUrl(filePath);

    return {
      success: true,
      filePath,
      publicUrl: publicUrlData.publicUrl
    };
  } catch (error) {
    console.error('Error uploading image:', error);
    return {
      success: false,
      error: error.message
    };
  }
}