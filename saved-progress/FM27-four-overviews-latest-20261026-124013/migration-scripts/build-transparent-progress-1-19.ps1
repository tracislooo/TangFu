$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Drawing;
using System.Drawing.Imaging;
public static class TransparentProgress {
 public static void Build(string input,string output) {
  Directory.CreateDirectory(output);
  using(var src=new Bitmap(input))
  using(var preview=new Bitmap(680,650))
  using(var g=Graphics.FromImage(preview))
  using(var font=new Font("Arial",12)) {
   if(src.Width!=196 || src.Height!=19) throw new Exception("Unexpected input size");
   g.Clear(Color.FromArgb(238,240,244));
   g.DrawString("Transparent PNG | 196 x 19 px | Fixed original gradient",font,Brushes.Black,12,12);
   string report="segment,percent,width,height,bar_width_px,unchanged_pixels,transparent_right_area\r\n";
   for(int n=1;n<=19;n++) {
    int width=(int)Math.Round(183*n/20.0,MidpointRounding.AwayFromZero);
    int end=6+width-1,capStart=end-4,count=0;
    using(var dst=new Bitmap(196,19,PixelFormat.Format32bppArgb)) {
     for(int y=0;y<19;y++) {
      double flatAlpha=0;
      for(int x=172;x<=180;x++) flatAlpha+=src.GetPixel(x,y).A;
      flatAlpha/=9;
      for(int x=0;x<capStart;x++) dst.SetPixel(x,y,src.GetPixel(x,y));
      for(int x=capStart;x<196 && x<=end+7;x++) {
       Color c=src.GetPixel(x,y),cap=src.GetPixel(188+(x-end),y);
       double coverage=flatAlpha>0 ? Math.Min(1,cap.A/flatAlpha) : 0;
       dst.SetPixel(x,y,Color.FromArgb((int)Math.Round(c.A*coverage),c.R,c.G,c.B));
      }
     }
     string name=String.Format("progress_{0:00}_of_20_{1:00}percent.png",n,n*5);
     string path=Path.Combine(output,name);
     dst.Save(path,ImageFormat.Png);
     using(var saved=new Bitmap(path)) {
      if(saved.Width!=196 || saved.Height!=19 || !Image.IsAlphaPixelFormat(saved.PixelFormat)) throw new Exception("PNG format mismatch");
      for(int y=0;y<19;y++) for(int x=0;x<capStart;x++) {
       if(saved.GetPixel(x,y).ToArgb()!=src.GetPixel(x,y).ToArgb()) throw new Exception("Original pixels changed");
       count++;
      }
      for(int y=0;y<19;y++) for(int x=end+8;x<196;x++)
       if(saved.GetPixel(x,y).A!=0) throw new Exception("Right region not transparent");
      for(int y=0;y<19;y++) for(int x=capStart;x<=end+7;x++) {
       var c=saved.GetPixel(x,y); var orig=src.GetPixel(x,y);
       if(c.A>0 && (c.R!=orig.R || c.G!=orig.G || c.B!=orig.B)) throw new Exception("Gradient recolored");
      }
      if(saved.GetPixel(195,0).A!=0 || saved.GetPixel(195,18).A!=0) throw new Exception("Opaque background");
     }
     int py=44+(n-1)*31;
     g.DrawString(String.Format("{0:00}/20 {1:00}%",n,n*5),font,Brushes.Black,14,py+4);
     for(int yy=0;yy<24;yy++) for(int xx=0;xx<25;xx++) {
      using(var brush=new SolidBrush((xx+yy)%2==0?Color.White:Color.FromArgb(213,216,222)))
       g.FillRectangle(brush,138+xx*16,py+yy,16,1);
     }
     g.InterpolationMode=System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor;
     g.PixelOffsetMode=System.Drawing.Drawing2D.PixelOffsetMode.Half;
     g.DrawImage(dst,new Rectangle(140,py+2,392,19),0,0,196,19,GraphicsUnit.Pixel);
     report+=String.Format("{0},{1},196,19,{2},{3},true\r\n",n,n*5,width,count);
    }
   }
   preview.Save(Path.Combine(output,"preview.png"),ImageFormat.Png);
   File.WriteAllText(Path.Combine(output,"verification.csv"),report);
   File.WriteAllText(Path.Combine(output,"README.txt"),"Input: K:/desktop/Group-54.png (original 196x19 RGBA PNG).\r\n19 PNGs at 5%-95%, same 196x19 canvas. Alpha transparency and original gradient retained.\r\nLeft anchor remains at x=6. Bar length rounded to nearest pixel from full width 183.\r\nAll original RGBA pixels before movable cap copied exactly. Only cap alpha is changed using source right cap coverage.\r\nAll nonzero-alpha output RGB values equal original RGB at the same coordinates.\r\nEmpty right area is fully transparent. Checkerboard exists only in preview.png.\r\n");
  }
 }
}
'@ -ReferencedAssemblies System.Drawing
[TransparentProgress]::Build('K:\桌面\组-54.png','G:\Doc\ChatGPT\New project\横向进度条-透明PNG-1至19段')
