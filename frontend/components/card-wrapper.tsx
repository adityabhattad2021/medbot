"use client"
import { Header } from "./header";
import { Button } from "./ui/button";
import { FcGoogle } from "react-icons/fc";
import { Card, CardContent, CardFooter, CardDescription, CardHeader } from "./ui/card";
import { Separator } from "./ui/separator";
import Link from "next/link";


interface CardWrapperProps {
    children: React.ReactNode;
    headerLabel: string;
    showSocial?: boolean;
    redirectUrl:string,
    redirectDescription:string,
    redirectLabel:string
};


export function CardWrapper({
    children,
    headerLabel,
    showSocial,
    redirectUrl,
    redirectDescription,
    redirectLabel
}: CardWrapperProps) {
    return (
        <Card className="w-[400px] shadow-md">
            <CardHeader>
                <Header label={headerLabel} />
            </CardHeader>
            <CardContent>
                {children}
            </CardContent>
            <CardFooter className="flex flex-col p-0">
                <CardDescription>
                    {redirectDescription}
                </CardDescription>
                <Button
                    variant={"link"}
                    className="font-normal w-full"
                    size={"sm"}
                    asChild
                >
                    <Link href={redirectUrl}>
                        {redirectLabel}
                    </Link>
                </Button>
            </CardFooter>
            <div className="w-full flex justify-center mb-2 text-muted-foreground text-xs">
                or
            </div>
            {showSocial && (
                <CardFooter className="flex flex-col gap-2">
                    <div className="flex items-center w-full gap-x-2">
                        <Button
                            size="lg"
                            className="w-full"
                            variant="outline"
                            onClick={() => { }}
                        >
                            <FcGoogle className="h-5 w-5 mr-4" />
                            Login with Google
                        </Button>
                    </div>
                </CardFooter>

            )}
            
        </Card>
    )
}