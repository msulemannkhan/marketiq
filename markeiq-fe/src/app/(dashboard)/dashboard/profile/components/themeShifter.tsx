import { Card, CardContent } from "@/components/ui/card";
import React, { useState, useEffect } from "react";

export default function ThemeShifter() {
    const [selectedTheme, setSelectedTheme] = useState<string>('');

    useEffect(() => {
        // Initialize theme from localStorage or system preference
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme && (storedTheme === 'light' || storedTheme === 'dark')) {
            setSelectedTheme(storedTheme);
            document.documentElement.classList.add(storedTheme);
        } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            setSelectedTheme('dark');
            document.documentElement.classList.add('dark');
        } else {
            setSelectedTheme('light');
            document.documentElement.classList.add('light');
        }
    }, []);

    useEffect(() => {
        // Apply theme whenever selectedTheme changes
        // Ensure only 'light' or 'dark' is applied
        document.documentElement.classList.remove('light', 'dark');
        if (selectedTheme === 'light' || selectedTheme === 'dark') {
            document.documentElement.classList.add(selectedTheme);
            localStorage.setItem('theme', selectedTheme);
        }
    }, [selectedTheme]);

    const handleThemeChange = (theme: string) => {
        setSelectedTheme(theme);
    };

    return (
        <Card>
            <CardContent>
                <div>
                    <p className="text-default-700 text-base font-medium">
                        Theme
                    </p>
                    <p className="text-default-400 mt-1 text-sm font-normal">
                        Change the appearance of the web.
                    </p>
                    <div
                        className="relative flex flex-col gap-2 mt-4 flex-wrap"
                        aria-label="Select theme"
                        role="radiogroup"
                        aria-orientation="horizontal"
                    >
                        <div
                            className="flex flex-col flex-wrap gap-2 data-[orientation=horizontal]:flex-row"
                            role="presentation"
                            data-orientation="horizontal"
                        >
                            {/* Light Theme Option */}
                            <label
                                className={`group hover:bg-content2 inline-flex flex-row-reverse justify-between rounded-large border-default-200 max-w-[300px] cursor-pointer gap-4 border-1 px-4 py-2.5 shadow-md relative h-[132px] flex-1 overflow-hidden ${
                                    selectedTheme === 'light' ? 'border-primary ring-2 ring-primary' : ''
                                }`}
                                data-selected={selectedTheme === 'light' ? 'true' : 'false'}
                            >
                                <div
                                    style={{
                                        border: "0px",
                                        clip: "rect(0px, 0px, 0px, 0px)",
                                        clipPath: "inset(50%)",
                                        height: "1px",
                                        margin: "-1px",
                                        overflow: "hidden",
                                        padding: "0px",
                                        position: "absolute",
                                        width: "1px",
                                        whiteSpace: "nowrap",
                                    }}
                                >
                                    <input
                                        aria-labelledby="light-theme-label"
                                        data-react-aria-pressable="true"
                                        tabIndex={0}
                                        className="font-inherit text-[100%] leading-[1.15] m-0 p-0 overflow-visible box-border absolute top-0 w-full h-full opacity-[0.0001] z-[1] cursor-pointer disabled:cursor-default"
                                        type="radio"
                                        value="light"
                                        name="theme-selector"
                                        checked={selectedTheme === 'light'}
                                        onChange={() => handleThemeChange('light')}
                                        title="Light Theme"
                                    />
                                </div>
                                <span
                                    aria-hidden="true"
                                    className="relative inline-flex items-center justify-center shrink-0 overflow-hidden border-solid box-border rounded-full group-data-[hover-unselected=true]:bg-default-100 outline-solid outline-transparent group-data-[focus-visible=true]:z-10 group-data-[focus-visible=true]:ring-2 group-data-[focus-visible=true]:ring-focus group-data-[focus-visible=true]:ring-offset-2 group-data-[focus-visible=true]:ring-offset-background w-5 h-5 group-data-[pressed=true]:scale-95 transition-transform-colors motion-reduce:transition-none border-default border-2 group-data-[selected=true]:border-default-foreground"
                                >
                                    <span className="bg-default-foreground text-primary-foreground transition-transform-opacity z-10 h-2 w-2 origin-center scale-0 rounded-full opacity-0 group-data-[selected=true]:scale-100 group-data-[selected=true]:opacity-100 motion-reduce:transition-none"></span>
                                </span>
                                <div className="flex flex-col ml-1 ms-2">
                                    <span
                                        id="light-theme-label"
                                        className="relative text-foreground select-none text-medium transition-colors motion-reduce:transition-none"
                                    >
                                        Light
                                    </span>
                                </div>
                                {/* Dark preview SVG (hidden) */}
                                <div className="absolute top-[37px] left-[32px] hidden">
                                    <svg
                                        fill="none"
                                        height="117"
                                        viewBox="0 0 240 117"
                                        width="240"
                                        xmlns="http://www.w3.org/2000/svg"
                                    >
                                        <path
                                            d="M12 0.5H228C234.351 0.5 239.5 5.64873 239.5 12V116.5H0.5V12C0.5 5.64873 5.64873 0.5 12 0.5Z"
                                            fill="black"
                                        ></path>
                                        <path
                                            d="M12 0.5H228C234.351 0.5 239.5 5.64873 239.5 12V116.5H0.5V12C0.5 5.64873 5.64873 0.5 12 0.5Z"
                                            stroke="#3F3F46"
                                        ></path>
                                        <path
                                            d="M32 48.5C32 45.4624 34.4624 43 37.5 43H67.5C70.5376 43 73 45.4624 73 48.5V48.5C73 51.5376 70.5376 54 67.5 54H37.5C34.4624 54 32 51.5376 32 48.5V48.5Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M17 105C17 101.686 19.6863 99 23 99H67C70.3137 99 73 101.686 73 105V105C73 108.314 70.3137 111 67 111H23C19.6863 111 17 108.314 17 105V105Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M88 25.5C88 22.4624 90.4624 20 93.5 20H207.5C210.538 20 213 22.4624 213 25.5V25.5C213 28.5376 210.538 31 207.5 31H93.5C90.4624 31 88 28.5376 88 25.5V25.5Z"
                                            fill="#3F3F46"
                                        ></path>
                                        <path
                                            d="M88 105C88 101.686 90.6863 99 94 99H189C192.314 99 195 101.686 195 105V105C195 108.314 192.314 111 189 111H94C90.6863 111 88 108.314 88 105V105Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M88 51C88 46.5817 91.5817 43 96 43H221C225.418 43 229 46.5817 229 51V85C229 89.4183 225.418 93 221 93H96C91.5817 93 88 89.4183 88 85V51Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M17 48.5C17 45.4624 19.4624 43 22.5 43V43C25.5376 43 28 45.4624 28 48.5V48.5C28 51.5376 25.5376 54 22.5 54V54C19.4624 54 17 51.5376 17 48.5V48.5Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M17 66.5C17 63.4624 19.4624 61 22.5 61V61C25.5376 61 28 63.4624 28 66.5V66.5C28 69.5376 25.5376 72 22.5 72V72C19.4624 72 17 69.5376 17 66.5V66.5Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M17 86.5C17 83.4624 19.4624 81 22.5 81V81C25.5376 81 28 83.4624 28 86.5V87.5C28 90.5376 25.5376 93 22.5 93V93C19.4624 93 17 90.5376 17 87.5V86.5Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M32 25.5C32 22.4624 34.4624 20 37.5 20H67.5C70.5376 20 73 22.4624 73 25.5V25.5C73 28.5376 70.5376 31 67.5 31H37.5C34.4624 31 32 28.5376 32 25.5V25.5Z"
                                            fill="#3F3F46"
                                        ></path>
                                        <path
                                            d="M32 66.5C32 63.4624 34.4624 61 37.5 61H67.5C70.5376 61 73 63.4624 73 66.5V66.5C73 69.5376 70.5376 72 67.5 72H37.5C34.4624 72 32 69.5376 32 66.5V66.5Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M32 87C32 83.6863 34.6863 81 38 81H67C70.3137 81 73 83.6863 73 87V87C73 90.3137 70.3137 93 67 93H38C34.6863 93 32 90.3137 32 87V87Z"
                                            fill="#27272A"
                                        ></path>
                                        <circle
                                            cx="22.5"
                                            cy="25.5"
                                            fill="#3F3F46"
                                            r="5.5"
                                        ></circle>
                                    </svg>
                                </div>
                                {/* Light preview SVG (visible) */}
                                <div className="absolute top-[37px] left-[32px]">
                                    <svg
                                        fill="none"
                                        height="117"
                                        viewBox="0 0 240 117"
                                        width="240"
                                        xmlns="http://www.w3.org/2000/svg"
                                    >
                                        <path
                                            d="M12 0.5H228C234.351 0.5 239.5 5.64873 239.5 12V116.5H0.5V12C0.5 5.64873 5.64873 0.5 12 0.5Z"
                                            fill="white"
                                        ></path>
                                        <path
                                            d="M12 0.5H228C234.351 0.5 239.5 5.64873 239.5 12V116.5H0.5V12C0.5 5.64873 5.64873 0.5 12 0.5Z"
                                            stroke="#E4E4E7"
                                        ></path>
                                        <path
                                            d="M32 48.5C32 45.4624 34.4624 43 37.5 43H67.5C70.5376 43 73 45.4624 73 48.5V48.5C73 51.5376 70.5376 54 67.5 54H37.5C34.4624 54 32 51.5376 32 48.5V48.5Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M17 105C17 101.686 19.6863 99 23 99H67C70.3137 99 73 101.686 73 105V105C73 108.314 70.3137 111 67 111H23C19.6863 111 17 108.314 17 105V105Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M88 25.5C88 22.4624 90.4624 20 93.5 20H207.5C210.538 20 213 22.4624 213 25.5V25.5C213 28.5376 210.538 31 207.5 31H93.5C90.4624 31 88 28.5376 88 25.5V25.5Z"
                                            fill="#E4E4E7"
                                        ></path>
                                        <path
                                            d="M88 105C88 101.686 90.6863 99 94 99H189C192.314 99 195 101.686 195 105V105C195 108.314 192.314 111 189 111H94C90.6863 111 88 108.314 88 105V105Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M88 51C88 46.5817 91.5817 43 96 43H221C225.418 43 229 46.5817 229 51V85C229 89.4183 225.418 93 221 93H96C91.5817 93 88 89.4183 88 85V51Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M17 48.5C17 45.4624 19.4624 43 22.5 43V43C25.5376 43 28 45.4624 28 48.5V48.5C28 51.5376 25.5376 54 22.5 54V54C19.4624 54 17 51.5376 17 48.5V48.5Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M17 66.5C17 63.4624 19.4624 61 22.5 61V61C25.5376 61 28 63.4624 28 66.5V66.5C28 69.5376 25.5376 72 22.5 72V72C19.4624 72 17 69.5376 17 66.5V66.5Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M17 86.5C17 83.4624 19.4624 81 22.5 81V81C25.5376 81 28 83.4624 28 86.5V87.5C28 90.5376 25.5376 93 22.5 93V93C19.4624 93 17 90.5376 17 87.5V86.5Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M32 25.5C32 22.4624 34.4624 20 37.5 20H67.5C70.5376 20 73 22.4624 73 25.5V25.5C73 28.5376 70.5376 31 67.5 31H37.5C34.4624 31 32 28.5376 32 25.5V25.5Z"
                                            fill="#E4E4E7"
                                        ></path>
                                        <path
                                            d="M32 66.5C32 63.4624 34.4624 61 37.5 61H67.5C70.5376 61 73 63.4624 73 66.5V66.5C73 69.5376 70.5376 72 67.5 72H37.5C34.4624 72 32 69.5376 32 66.5V66.5Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M32 87C32 83.6863 34.6863 81 38 81H67C70.3137 81 73 83.6863 73 87V87C73 90.3137 70.3137 93 67 93H38C34.6863 93 32 90.3137 32 87V87Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <circle
                                            cx="22.5"
                                            cy="25.5"
                                            fill="#E4E4E7"
                                            r="5.5"
                                        ></circle>
                                    </svg>
                                </div>
                            </label>

                            {/* Dark Theme Option */}
                            <label
                                className={`group hover:bg-content2 inline-flex flex-row-reverse justify-between rounded-large border-default-200 max-w-[300px] cursor-pointer gap-4 border-1 px-4 py-2.5 shadow-md relative h-[132px] flex-1 overflow-hidden ${
                                    selectedTheme === 'dark' ? 'border-primary ring-2 ring-primary' : ''
                                }`}
                                data-selected={selectedTheme === 'dark' ? 'true' : 'false'}
                            >
                                <div
                                    style={{
                                        border: "0px",
                                        clip: "rect(0px, 0px, 0px, 0px)",
                                        clipPath: "inset(50%)",
                                        height: "1px",
                                        margin: "-1px",
                                        overflow: "hidden",
                                        padding: "0px",
                                        position: "absolute",
                                        width: "1px",
                                        whiteSpace: "nowrap",
                                    }}
                                >
                                    <input
                                        aria-labelledby="dark-theme-label"
                                        data-react-aria-pressable="true"
                                        tabIndex={0}
                                        className="font-inherit text-[100%] leading-[1.15] m-0 p-0 overflow-visible box-border absolute top-0 w-full h-full opacity-[0.0001] z-[1] cursor-pointer disabled:cursor-default"
                                        type="radio"
                                        value="dark"
                                        name="theme-selector"
                                        checked={selectedTheme === 'dark'}
                                        onChange={() => handleThemeChange('dark')}
                                        title="Dark Theme"
                                    />
                                </div>
                                <span
                                    aria-hidden="true"
                                    className="relative inline-flex items-center justify-center shrink-0 overflow-hidden border-solid box-border rounded-full group-data-[hover-unselected=true]:bg-default-100 outline-solid outline-transparent group-data-[focus-visible=true]:z-10 group-data-[focus-visible=true]:ring-2 group-data-[focus-visible=true]:ring-focus group-data-[focus-visible=true]:ring-offset-2 group-data-[focus-visible=true]:ring-offset-background w-5 h-5 group-data-[pressed=true]:scale-95 transition-transform-colors motion-reduce:transition-none border-default border-2 group-data-[selected=true]:border-default-foreground"
                                >
                                    <span className="bg-default-foreground text-primary-foreground transition-transform-opacity z-10 h-2 w-2 origin-center scale-0 rounded-full opacity-0 group-data-[selected=true]:scale-100 group-data-[selected=true]:opacity-100 motion-reduce:transition-none"></span>
                                </span>
                                <div className="flex flex-col ml-1 ms-2">
                                    <span
                                        id="dark-theme-label"
                                        className="relative text-foreground select-none text-medium transition-colors motion-reduce:transition-none"
                                    >
                                        Dark
                                    </span>
                                </div>
                                {/* Dark preview SVG (visible) */}
                                <div className="absolute top-[37px] left-[32px]">
                                    <svg
                                        fill="none"
                                        height="117"
                                        viewBox="0 0 240 117"
                                        width="240"
                                        xmlns="http://www.w3.org/2000/svg"
                                    >
                                        <path
                                            d="M12 0.5H228C234.351 0.5 239.5 5.64873 239.5 12V116.5H0.5V12C0.5 5.64873 5.64873 0.5 12 0.5Z"
                                            fill="black"
                                        ></path>
                                        <path
                                            d="M12 0.5H228C234.351 0.5 239.5 5.64873 239.5 12V116.5H0.5V12C0.5 5.64873 5.64873 0.5 12 0.5Z"
                                            stroke="#3F3F46"
                                        ></path>
                                        <path
                                            d="M32 48.5C32 45.4624 34.4624 43 37.5 43H67.5C70.5376 43 73 45.4624 73 48.5V48.5C73 51.5376 70.5376 54 67.5 54H37.5C34.4624 54 32 51.5376 32 48.5V48.5Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M17 105C17 101.686 19.6863 99 23 99H67C70.3137 99 73 101.686 73 105V105C73 108.314 70.3137 111 67 111H23C19.6863 111 17 108.314 17 105V105Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M88 25.5C88 22.4624 90.4624 20 93.5 20H207.5C210.538 20 213 22.4624 213 25.5V25.5C213 28.5376 210.538 31 207.5 31H93.5C90.4624 31 88 28.5376 88 25.5V25.5Z"
                                            fill="#3F3F46"
                                        ></path>
                                        <path
                                            d="M88 105C88 101.686 90.6863 99 94 99H189C192.314 99 195 101.686 195 105V105C195 108.314 192.314 111 189 111H94C90.6863 111 88 108.314 88 105V105Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M88 51C88 46.5817 91.5817 43 96 43H221C225.418 43 229 46.5817 229 51V85C229 89.4183 225.418 93 221 93H96C91.5817 93 88 89.4183 88 85V51Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M17 48.5C17 45.4624 19.4624 43 22.5 43V43C25.5376 43 28 45.4624 28 48.5V48.5C28 51.5376 25.5376 54 22.5 54V54C19.4624 54 17 51.5376 17 48.5V48.5Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M17 66.5C17 63.4624 19.4624 61 22.5 61V61C25.5376 61 28 63.4624 28 66.5V66.5C28 69.5376 25.5376 72 22.5 72V72C19.4624 72 17 69.5376 17 66.5V66.5Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M17 86.5C17 83.4624 19.4624 81 22.5 81V81C25.5376 81 28 83.4624 28 86.5V87.5C28 90.5376 25.5376 93 22.5 93V93C19.4624 93 17 90.5376 17 87.5V86.5Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M32 25.5C32 22.4624 34.4624 20 37.5 20H67.5C70.5376 20 73 22.4624 73 25.5V25.5C73 28.5376 70.5376 31 67.5 31H37.5C34.4624 31 32 28.5376 32 25.5V25.5Z"
                                            fill="#3F3F46"
                                        ></path>
                                        <path
                                            d="M32 66.5C32 63.4624 34.4624 61 37.5 61H67.5C70.5376 61 73 63.4624 73 66.5V66.5C73 69.5376 70.5376 72 67.5 72H37.5C34.4624 72 32 69.5376 32 66.5V66.5Z"
                                            fill="#27272A"
                                        ></path>
                                        <path
                                            d="M32 87C32 83.6863 34.6863 81 38 81H67C70.3137 81 73 83.6863 73 87V87C73 90.3137 70.3137 93 67 93H38C34.6863 93 32 90.3137 32 87V87Z"
                                            fill="#27272A"
                                        ></path>
                                        <circle
                                            cx="22.5"
                                            cy="25.5"
                                            fill="#3F3F46"
                                            r="5.5"
                                        ></circle>
                                    </svg>
                                </div>
                                {/* Light preview SVG (hidden) */}
                                <div className="absolute top-[37px] left-[32px] hidden">
                                    <svg
                                        fill="none"
                                        height="117"
                                        viewBox="0 0 240 117"
                                        width="240"
                                        xmlns="http://www.w3.org/2000/svg"
                                    >
                                        <path
                                            d="M12 0.5H228C234.351 0.5 239.5 5.64873 239.5 12V116.5H0.5V12C0.5 5.64873 5.64873 0.5 12 0.5Z"
                                            fill="white"
                                        ></path>
                                        <path
                                            d="M12 0.5H228C234.351 0.5 239.5 5.64873 239.5 12V116.5H0.5V12C0.5 5.64873 5.64873 0.5 12 0.5Z"
                                            stroke="#E4E4E7"
                                        ></path>
                                        <path
                                            d="M32 48.5C32 45.4624 34.4624 43 37.5 43H67.5C70.5376 43 73 45.4624 73 48.5V48.5C73 51.5376 70.5376 54 67.5 54H37.5C34.4624 54 32 51.5376 32 48.5V48.5Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M17 105C17 101.686 19.6863 99 23 99H67C70.3137 99 73 101.686 73 105V105C73 108.314 70.3137 111 67 111H23C19.6863 111 17 108.314 17 105V105Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M88 25.5C88 22.4624 90.4624 20 93.5 20H207.5C210.538 20 213 22.4624 213 25.5V25.5C213 28.5376 210.538 31 207.5 31H93.5C90.4624 31 88 28.5376 88 25.5V25.5Z"
                                            fill="#E4E4E7"
                                        ></path>
                                        <path
                                            d="M88 105C88 101.686 90.6863 99 94 99H189C192.314 99 195 101.686 195 105V105C195 108.314 192.314 111 189 111H94C90.6863 111 88 108.314 88 105V105Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M88 51C88 46.5817 91.5817 43 96 43H221C225.418 43 229 46.5817 229 51V85C229 89.4183 225.418 93 221 93H96C91.5817 93 88 89.4183 88 85V51Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M17 48.5C17 45.4624 19.4624 43 22.5 43V43C25.5376 43 28 45.4624 28 48.5V48.5C28 51.5376 25.5376 54 22.5 54V54C19.4624 54 17 51.5376 17 48.5V48.5Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M17 66.5C17 63.4624 19.4624 61 22.5 61V61C25.5376 61 28 63.4624 28 66.5V66.5C28 69.5376 25.5376 72 22.5 72V72C19.4624 72 17 69.5376 17 66.5V66.5Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M17 86.5C17 83.4624 19.4624 81 22.5 81V81C25.5376 81 28 83.4624 28 86.5V87.5C28 90.5376 25.5376 93 22.5 93V93C19.4624 93 17 90.5376 17 87.5V86.5Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M32 25.5C32 22.4624 34.4624 20 37.5 20H67.5C70.5376 20 73 22.4624 73 25.5V25.5C73 28.5376 70.5376 31 67.5 31H37.5C34.4624 31 32 28.5376 32 25.5V25.5Z"
                                            fill="#E4E4E7"
                                        ></path>
                                        <path
                                            d="M32 66.5C32 63.4624 34.4624 61 37.5 61H67.5C70.5376 61 73 63.4624 73 66.5V66.5C73 69.5376 70.5376 72 67.5 72H37.5C34.4624 72 32 69.5376 32 66.5V66.5Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <path
                                            d="M32 87C32 83.6863 34.6863 81 38 81H67C70.3137 81 73 83.6863 73 87V87C73 90.3137 70.3137 93 67 93H38C34.6863 93 32 90.3137 32 87V87Z"
                                            fill="#F4F4F5"
                                        ></path>
                                        <circle
                                            cx="22.5"
                                            cy="25.5"
                                            fill="#E4E4E7"
                                            r="5.5"
                                        ></circle>
                                    </svg>
                                </div>
                            </label>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
