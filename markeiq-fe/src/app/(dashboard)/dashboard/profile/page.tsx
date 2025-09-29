"use client";

import { useState, useEffect } from "react";
import { useAppDispatch, useAppSelector } from "@/lib/redux/hooks";
import { getCurrentUser, updateProfile } from "@/lib/redux/slices/authSlice";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Spinner } from "@heroui/react";
import {
    User,
    Mail,
    Calendar,
    Globe,
    Edit3,
    Save,
    X,
    Clock,
    Shield,
    CheckCircle2,
    AlertCircle,
    Camera,
} from "lucide-react";
import { Loader } from "@/lib/components";
import ThemeShifter from "./components/themeShifter";
import Image from "next/image";

export default function ProfilePage() {
    const dispatch = useAppDispatch();
    const { user, isLoading } = useAppSelector((state) => state.auth);
    const [isEditing, setIsEditing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [formData, setFormData] = useState({
        full_name: "",
        bio: "",
        timezone: "",
        avatar_url: "",
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    useEffect(() => {
        if (user) {
            setFormData({
                full_name: user.full_name || "",
                bio: user.bio || "",
                timezone: user.timezone || "UTC",
                avatar_url: user.avatar_url || "",
            });
        }
    }, [user]);

    useEffect(() => {
        dispatch(getCurrentUser());
    }, [dispatch]);

    const handleInputChange =
        (field: keyof typeof formData) =>
        (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
            setFormData((prev) => ({ ...prev, [field]: e.target.value }));
            // Clear error when user starts typing
            if (errors[field]) {
                setErrors((prev) => ({ ...prev, [field]: "" }));
            }
        };

    const validateForm = () => {
        const newErrors: Record<string, string> = {};

        if (!formData.full_name.trim()) {
            newErrors.full_name = "Full name is required";
        }

        if (formData.bio && formData.bio.length > 500) {
            newErrors.bio = "Bio must be less than 500 characters";
        }

        if (formData.avatar_url && !isValidUrl(formData.avatar_url)) {
            newErrors.avatar_url = "Please enter a valid URL";
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const isValidUrl = (url: string) => {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    };

    const handleSave = async () => {
        if (!validateForm()) return;

        setIsSaving(true);
        try {
            const result = await dispatch(updateProfile(formData));
            if (updateProfile.fulfilled.match(result)) {
                setIsEditing(false);
                setErrors({});
            } else if (updateProfile.rejected.match(result)) {
                setErrors({ general: result.payload as string });
            }
        } catch {
            setErrors({ general: "Failed to update profile" });
        } finally {
            setIsSaving(false);
        }
    };

    const handleCancel = () => {
        if (user) {
            setFormData({
                full_name: user.full_name || "",
                bio: user.bio || "",
                timezone: user.timezone || "UTC",
                avatar_url: user.avatar_url || "",
            });
        }
        setIsEditing(false);
        setErrors({});
    };

    const timezoneOptions = [
        { value: "UTC", label: "UTC (Coordinated Universal Time)" },
        { value: "America/New_York", label: "Eastern Time (ET)" },
        { value: "America/Chicago", label: "Central Time (CT)" },
        { value: "America/Denver", label: "Mountain Time (MT)" },
        { value: "America/Los_Angeles", label: "Pacific Time (PT)" },
        { value: "Europe/London", label: "London (GMT/BST)" },
        { value: "Europe/Paris", label: "Paris (CET/CEST)" },
        { value: "Asia/Tokyo", label: "Tokyo (JST)" },
        { value: "Asia/Shanghai", label: "Shanghai (CST)" },
        { value: "Australia/Sydney", label: "Sydney (AEST/AEDT)" },
    ];

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="flex flex-col items-center gap-4">
                    <Spinner size="lg" />
                    <p className="text-sm text-muted-foreground">
                        Loading your profile...
                    </p>
                </div>
            </div>
        );
    }

    if (!user) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Card className="w-full max-w-md">
                    <CardContent className="pt-6">
                        <div className="text-center space-y-4">
                            <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto" />
                            <div>
                                <h2 className="text-xl font-semibold">
                                    User not found
                                </h2>
                                <p className="text-sm text-muted-foreground mt-2">
                                    Please log in to view your profile.
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    }

    const avatarUrl =
        user.avatar_url ||
        `https://ui-avatars.com/api/?name=${encodeURIComponent(
            user.full_name || user.username
        )}&background=random&color=fff`;

    return (
        <div className="container mx-auto px-4 py-8 max-w-6xl">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        Profile Settings
                    </h1>
                    <p className="text-muted-foreground">
                        Manage your account information and preferences
                    </p>
                </div>
                {!isEditing ? (
                    <Button
                        onClick={() => setIsEditing(true)}
                        className="w-fit"
                    >
                        <Edit3 className="w-4 h-4 mr-2" />
                        Edit Profile
                    </Button>
                ) : (
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            onClick={handleCancel}
                            disabled={isSaving}
                        >
                            <X className="w-4 h-4 mr-2" />
                            Cancel
                        </Button>
                        <Button onClick={handleSave} disabled={isSaving}>
                            {isSaving ? (
                                <Loader />
                            ) : (
                                <Save className="w-4 h-4 mr-2" />
                            )}
                            Save Changes
                        </Button>
                    </div>
                )}
            </div>

            {/* Error Alert */}
            {errors.general && (
                <Card className="border-destructive mb-6">
                    <CardContent className="pt-4">
                        <div className="flex items-center gap-2 text-destructive">
                            <AlertCircle className="w-4 h-4" />
                            <p className="text-sm font-medium">
                                {errors.general}
                            </p>
                        </div>
                    </CardContent>
                </Card>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Profile Overview */}
                <div className="lg:col-span-1">
                    <Card>
                        <CardContent className="pt-6">
                            <div className="flex flex-col items-center text-center space-y-4">
                                <div className="relative">
                                    <div className="w-24 h-24 rounded-full overflow-hidden border-4 border-background shadow-lg">
                                        <Image
                                            src={avatarUrl}
                                            alt={
                                                user.full_name || user.username
                                            }
                                            width={96}
                                            height={96}
                                            className="w-full h-full object-cover"
                                        />
                                    </div>
                                    {isEditing && (
                                        <div className="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center cursor-pointer">
                                            <Camera className="w-5 h-5 text-white" />
                                        </div>
                                    )}
                                </div>

                                <div className="space-y-1">
                                    <h3 className="text-lg font-semibold">
                                        {user.full_name || user.username}
                                    </h3>
                                    <p className="text-sm text-muted-foreground">
                                        @{user.username}
                                    </p>
                                </div>

                                {user.bio && (
                                    <p className="text-sm text-muted-foreground leading-relaxed">
                                        {user.bio}
                                    </p>
                                )}

                                <Separator />

                                <div className="flex flex-wrap gap-2 justify-center">
                                    <Badge
                                        variant={
                                            user.is_active
                                                ? "default"
                                                : "secondary"
                                        }
                                        className="text-xs"
                                    >
                                        {user.is_active ? (
                                            <>
                                                <CheckCircle2 className="w-3 h-3 mr-1" />
                                                Active
                                            </>
                                        ) : (
                                            <>
                                                <AlertCircle className="w-3 h-3 mr-1" />
                                                Inactive
                                            </>
                                        )}
                                    </Badge>
                                    <Badge
                                        variant={
                                            user.is_verified
                                                ? "default"
                                                : "outline"
                                        }
                                        className="text-xs"
                                    >
                                        {user.is_verified ? (
                                            <>
                                                <Shield className="w-3 h-3 mr-1" />
                                                Verified
                                            </>
                                        ) : (
                                            <>
                                                <AlertCircle className="w-3 h-3 mr-1" />
                                                Unverified
                                            </>
                                        )}
                                    </Badge>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Main Content */}
                <div className="lg:col-span-3 space-y-6">
                    {/* Personal Information */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <User className="w-5 h-5" />
                                Personal Information
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <Label
                                        htmlFor="email"
                                        className="text-sm font-medium"
                                    >
                                        Email Address
                                    </Label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                                        <Input
                                            id="email"
                                            value={user.email}
                                            disabled
                                            className="pl-10"
                                        />
                                    </div>
                                    <p className="text-xs text-muted-foreground">
                                        Email address cannot be changed
                                    </p>
                                </div>

                                <div className="space-y-2">
                                    <Label
                                        htmlFor="username"
                                        className="text-sm font-medium"
                                    >
                                        Username
                                    </Label>
                                    <div className="relative">
                                        <User className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                                        <Input
                                            id="username"
                                            value={`@${user.username}`}
                                            disabled
                                            className="pl-10"
                                        />
                                    </div>
                                    <p className="text-xs text-muted-foreground">
                                        Username cannot be changed
                                    </p>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label
                                    htmlFor="full_name"
                                    className="text-sm font-medium"
                                >
                                    Full Name
                                </Label>
                                <Input
                                    id="full_name"
                                    value={
                                        isEditing
                                            ? formData.full_name
                                            : user.full_name || ""
                                    }
                                    onChange={
                                        isEditing
                                            ? handleInputChange("full_name")
                                            : undefined
                                    }
                                    disabled={!isEditing}
                                    placeholder="Enter your full name"
                                    className={
                                        errors.full_name
                                            ? "border-destructive"
                                            : ""
                                    }
                                />
                                {errors.full_name && (
                                    <p className="text-xs text-destructive">
                                        {errors.full_name}
                                    </p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label
                                    htmlFor="bio"
                                    className="text-sm font-medium"
                                >
                                    Bio
                                </Label>
                                {isEditing ? (
                                    <Textarea
                                        id="bio"
                                        value={formData.bio}
                                        onChange={handleInputChange("bio")}
                                        placeholder="Tell us about yourself..."
                                        rows={3}
                                        className={`resize-none ${
                                            errors.bio
                                                ? "border-destructive"
                                                : ""
                                        }`}
                                    />
                                ) : (
                                    <Input
                                        id="bio"
                                        value={user.bio || "No bio provided"}
                                        disabled
                                    />
                                )}
                                {isEditing && (
                                    <p className="text-xs text-muted-foreground">
                                        {formData.bio.length}/500 characters
                                    </p>
                                )}
                                {errors.bio && (
                                    <p className="text-xs text-destructive">
                                        {errors.bio}
                                    </p>
                                )}
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <Label
                                        htmlFor="timezone"
                                        className="text-sm font-medium"
                                    >
                                        Timezone
                                    </Label>
                                    {isEditing ? (
                                        <Select
                                            value={formData.timezone}
                                            onValueChange={(value) =>
                                                setFormData((prev) => ({
                                                    ...prev,
                                                    timezone: value,
                                                }))
                                            }
                                        >
                                            <SelectTrigger>
                                                <Globe className="w-4 h-4 mr-2" />
                                                <SelectValue placeholder="Select timezone" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {timezoneOptions.map((tz) => (
                                                    <SelectItem
                                                        key={tz.value}
                                                        value={tz.value}
                                                    >
                                                        {tz.label}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    ) : (
                                        <div className="relative">
                                            <Globe className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                                            <Input
                                                value={
                                                    timezoneOptions.find(
                                                        (tz) =>
                                                            tz.value ===
                                                            user.timezone
                                                    )?.label || user.timezone
                                                }
                                                disabled
                                                className="pl-10"
                                            />
                                        </div>
                                    )}
                                </div>

                                <div className="space-y-2">
                                    <Label
                                        htmlFor="avatar_url"
                                        className="text-sm font-medium"
                                    >
                                        Avatar URL
                                    </Label>
                                    <Input
                                        id="avatar_url"
                                        value={
                                            isEditing
                                                ? formData.avatar_url
                                                : user.avatar_url || ""
                                        }
                                        onChange={
                                            isEditing
                                                ? handleInputChange(
                                                      "avatar_url"
                                                  )
                                                : undefined
                                        }
                                        disabled={!isEditing}
                                        placeholder="https://example.com/avatar.jpg"
                                        className={
                                            errors.avatar_url
                                                ? "border-destructive"
                                                : ""
                                        }
                                    />
                                    {errors.avatar_url && (
                                        <p className="text-xs text-destructive">
                                            {errors.avatar_url}
                                        </p>
                                    )}
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Account Information */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Shield className="w-5 h-5" />
                                Account Information
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <Label className="text-sm font-medium">
                                        Member Since
                                    </Label>
                                    <div className="relative">
                                        <Calendar className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                                        <Input
                                            value={new Date(
                                                user.created_at
                                            ).toLocaleDateString("en-US", {
                                                year: "numeric",
                                                month: "long",
                                                day: "numeric",
                                            })}
                                            disabled
                                            className="pl-10"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label className="text-sm font-medium">
                                        Last Login
                                    </Label>
                                    <div className="relative">
                                        <Clock className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                                        <Input
                                            value={new Date(
                                                user.last_login_at
                                            ).toLocaleString("en-US", {
                                                year: "numeric",
                                                month: "short",
                                                day: "numeric",
                                                hour: "2-digit",
                                                minute: "2-digit",
                                            })}
                                            disabled
                                            className="pl-10"
                                        />
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    {/* Theme Shiter */}
                    <ThemeShifter />
                </div>
            </div>
        </div>
    );
}
