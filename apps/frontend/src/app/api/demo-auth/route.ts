import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { code } = body;

    const expectedCode = process.env.DEMO_ACCESS_CODE || 'gourmet2026';

    if (!code || typeof code !== 'string' || code.trim() !== expectedCode.trim()) {
      return NextResponse.json(
        { error: 'Invalid demo access code. Please verify and try again.' },
        { status: 401 }
      );
    }

    const response = NextResponse.json({ success: true, message: 'Access granted' });

    // Set demo session cookie across all protocols and tunnels
    response.cookies.set('demo_session', 'authenticated', {
      httpOnly: false,
      secure: false,
      sameSite: 'lax',
      path: '/',
      maxAge: 60 * 60 * 24 * 7, // 7 days
    });

    return response;
  } catch {
    return NextResponse.json(
      { error: 'Invalid request payload.' },
      { status: 400 }
    );
  }
}

export async function DELETE() {
  const response = NextResponse.json({ success: true, message: 'Signed out' });
  response.cookies.delete('demo_session');
  return response;
}
