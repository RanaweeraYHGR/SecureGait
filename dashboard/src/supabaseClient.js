import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://ftioxcgnobztqbuyhihc.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ0aW94Y2dub2J6dHFidXloaWhjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4MjIwMTYsImV4cCI6MjA2NzM5ODAxNn0.7dcKOAL6-znVVIGXt5o2SJdNVVHm0MpZm152Gq34Ygw'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)